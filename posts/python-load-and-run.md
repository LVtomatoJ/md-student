---
create_time: 2025-05-10 16:21:00
tags: python
title: "apscheduler定时运行指定py脚本"
update_time: 2025-05-10 16:21:00

---

# Python apscheduler定时运行指定py脚本

先说一下需求背景,原本是想要写一个简单的定时追踪任务,比如每过一天跑一个脚本获取一下某个页面的指定位置的数值，然后存储起来在前端进行数据分析。其实就是scrapy的mini优化版hh，为了做的可扩展完成了上传python代码并在指定时间运行的定时任务,因为一般开发都是import需要的模块但是我的需求是引入是动态的,可能这个py文件叫abc.py也可能叫123.py，以前看到过但是没有自己做过所以尝试一下顺便记录一下相关的知识。

## 1、方案对比

了解到有两种方式可以调用制定的脚本但是两者之间略有不同.

- [importlib](https://docs.python.org/zh-cn/3.11/library/importlib.html)
- [runpy](https://docs.python.org/zh-cn/3.11/library/runpy.html)

| 功能         | `importlib`                    | `runpy`                          |
| ---------- | ------------------------------ | -------------------------------- |
| 导入模块       | ✅ 动态导入模块                       | 🚫 不专门用于导入                       |
| 执行模块       | ⚠️ 需要手动调用函数等                   | ✅ 直接运行模块或脚本                      |
| 支持路径加载     | ✅ `spec_from_file_location`等方式 | ✅ `run_path()` 支持路径加载            |
| 获取变量       | 🚫 直接导入不返回命名空间字典               | ✅ 返回一个字典，包含变量                    |
| 类似 `-m` 调用 | 🚫                             | ✅ `run_module()` 相当于 `python -m` |

```Python
# runpy demo
import runpy

runpy.run_path("tasks/my_task.py")

# importlib demo

import importlib.util

def load_module_from_path(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

mod = load_module_from_path("tasks/my_task.py", "my_task")
mod.run_task(arg1=123)
```

简单对比就可以发现runpy其实更加简单但是自由度会低一些因为它会直接运行python文件,而importlib调用会稍微复杂一些但是相对的它会更灵活一些,参考以前写过一些serverless,大多都会有一个入口函数所以权衡之下最后还是选择了importlib的方案！后续优化应该会有更多的空间。

## 2、封装

因为本质还是一个定时任务,所以有一个[apscheduler](https://apscheduler.readthedocs.io/en/3.x/)的封装

```Python
class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._running_jobs = set()

    async def start(self):
        self.scheduler.configure(timezone='Asia/Shanghai')
        self.scheduler.start()
        await self.load_all_tasks()

    async def stop(self):
        self.scheduler.shutdown()
```

后续的演示中函数都是TaskScheduler类中的咯

### 读库

init时需要从数据库读出task表中所有的任务并判断是否启动

```Python
# load_all_tasks
async def load_all_tasks(self):
    session = next(get_session())
    try:
        tasks = session.exec(select(Task)).all()
        for task in tasks:
            if task.running:
                await self.add_task(task)
    finally:
        session.close()
```

这部分很简单就是读库然后如果running为true就调用add_task创建定时任务

### add_task

```Python
async def add_task(self, task: Task):
    if str(task.id) in self._running_jobs:
        return

    func = self._load_task_function(task.id)
    if func is None:
        return

    try:
        self.scheduler.add_job(
            self._execute_task,
            CronTrigger.from_crontab(task.cron_expression),
            id=str(task.id),
            replace_existing=True,
            args=[task.id, func],
            misfire_grace_time=None
        )
        self._running_jobs.add(str(task.id))
        logger.info(f"Task {task.id} added to scheduler")
    except Exception as e:
        logger.error(f"Error adding task {task.id} to scheduler: {str(e)}")
```

这里可以看到scheduler.add_job第一个参数是_execute_task对应的参数为task_id和func,这里没有直接写对应脚本的run函数是因为有获取到返回值并保存到数据库的需求。
func是从_load_task_function的返回值他会用importlib加载对应的python文件并返回run方法，下面是这两部分的实现

### _load_task_function

```Python
def _load_task_function(self, task_id: int) -> Optional[callable]:
    try:
        file_path = Path(f'app/functions/{task_id}.py')
        if not file_path.exists():
            logger.error(f"Task file not found: {file_path}")
            return None

        spec = importlib.util.spec_from_file_location(f"task_{task_id}", file_path)
        if spec is None or spec.loader is None:
            logger.error(f"Failed to load spec for task {task_id}")
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        if not hasattr(module, 'run'):
            logger.error(f"Task {task_id} has no run function")
            return None

        return module.run
    except Exception as e:
        logger.error(f"Error loading task {task_id}: {str(e)}")
        return None
```

这里参考了importlib中直接导入源码文件的部分代码

1. spec_from_file_location根据路径读取到文件创建了[MoudleSpec实例](https://docs.python.org/zh-cn/3.11/library/importlib.html#importlib.machinery.ModuleSpec)
2. module_from_spec根据spec创建了模块对象，并执行了模块的代码，这里就是加载了python文件并返回了run方法

ModuleSpec->针对特定模块的导入系统相关状态的规范说明(好长..但是就当他是个说明好了)

接下来说一下
`if spec is None or spec.loader is None`
这个判断 可以把importlib当作一个快递员，spec就是对应的快递单，loader就是送货的卡车(用于真的加载代码)，如果文件存在但是里面没有代码或者没有权限或者根本跑不了这种情况就会导致loder是None,所以这两个检查都是必要的(除非你喜欢写try-catch)

这里贴一下spec_from_file_location的源码

```Python
def spec_from_file_location(name, location=None, *, loader=None,
                            submodule_search_locations=_POPULATE):
    """Return a module spec based on a file location.

    To indicate that the module is a package, set
    submodule_search_locations to a list of directory paths.  An
    empty list is sufficient, though its not otherwise useful to the
    import system.

    The loader must take a spec as its only __init__() arg.

    """
    if location is None:
        # The caller may simply want a partially populated location-
        # oriented spec.  So we set the location to a bogus value and
        # fill in as much as we can.
        location = '<unknown>'
        if hasattr(loader, 'get_filename'):
            # ExecutionLoader
            try:
                location = loader.get_filename(name)
            except ImportError:
                pass
    else:
        location = _os.fspath(location)
        try:
            location = _path_abspath(location)
        except OSError:
            pass

    # If the location is on the filesystem, but doesn't actually exist,
    # we could return None here, indicating that the location is not
    # valid.  However, we don't have a good way of testing since an
    # indirect location (e.g. a zip file or URL) will look like a
    # non-existent file relative to the filesystem.

    spec = _bootstrap.ModuleSpec(name, loader, origin=location)
    spec._set_fileattr = True

    # Pick a loader if one wasn't provided.
    if loader is None:
        for loader_class, suffixes in _get_supported_file_loaders():
            if location.endswith(tuple(suffixes)):
                loader = loader_class(name, location)
                spec.loader = loader
                break
        else:
            return None

    # Set submodule_search_paths appropriately.
    if submodule_search_locations is _POPULATE:
        # Check the loader.
        if hasattr(loader, 'is_package'):
            try:
                is_package = loader.is_package(name)
            except ImportError:
                pass
            else:
                if is_package:
                    spec.submodule_search_locations = []
    else:
        spec.submodule_search_locations = submodule_search_locations
    if spec.submodule_search_locations == []:
        if location:
            dirname = _path_split(location)[0]
            spec.submodule_search_locations.append(dirname)

    return spec
```

可以发现几个很有意思的地方

- 可以自己传入loader
- 可以从网络加载python代码(后续支持对象存储！)
- 如果没有传入会调用_get_supported_file_loaders选择适合的loader

意外之喜给后续的优化做好了铺垫，_get_supported_file_loaders中返回了三个loader的数组对应如下

| 类型          | 加载器                  | 文件后缀示例     | 用途                      |
| ------------- | ----------------------- | --------------- | ------------------------- |
| C 扩展模块     | ExtensionFileLoader     | .so, .pyd       | 加载 C/C++ 编写的扩展      |
| Python 源代码  | SourceFileLoader        | .py            | 加载普通 Python 代码       |
| Python 字节码  | SourcelessFileLoader    | .pyc           | 加载预编译的字节码缓存     |

- 所以如果运行过的话把目录指定到 /__pycache__/ 下可能会更高效？

ok发散就到这里

### _execute_task

运行指定函数的封装

```python
async def _execute_task(self, task_id: int, func: callable):
    session = next(get_session())
    try:
        task = session.get(Task, task_id)
        if not task:
            logger.error(f"Task {task_id} not found in database")
            return
        if not task.running:
            logger.info(f"Task {task_id} is stop")
            await self.remove_task(task_id)
            return

        run_log = TaskRunLog(task_id=task_id, status="running")
        session.add(run_log)
        session.commit()
        logger.info(f"Created run log for task {task_id}")

        try:
            result = await func()
            logger.info(f"Task {task_id} result: {result}")

            if task.have_return_value and result is not None:
                try:
                    if isinstance(result, (dict, list)):
                        run_log.return_value = json.dumps(result)
                    else:
                        run_log.return_value = str(result)
                except Exception as e:
                    logger.error(f"Failed to serialize task result: {str(e)}")
                    run_log.return_value = str(result)

            run_log.status = "success"
            session.add(run_log)
            session.commit()
            session.refresh(run_log)

        except Exception as e:
            run_log.status = "error"
            run_log.error = str(e)
            logger.error(f"Task {task_id} execution failed: {str(e)}")
            session.add(run_log)
            session.commit()

        logger.info(f"Updated run log for task {task_id} with status: {run_log.status}")

    except Exception as e:
        logger.error(f"Error handling task {task_id}: {str(e)}")
    finally:
        session.close()
```

这里把任务的返回值保存在了run_log的表中了方便后续进行追踪

这样就实现好了基本的功能 后端fastapi前端vue一把梭了.

## 总结

动态加载应用在公司项目数据库部分由应用到,当时看到了觉得很神奇,因为大部分时间是接触不到这种需求的,所以就一直没去尝试过,借着自己做小项目的机会尝试了一下还是很有趣的，可以发挥的空间还很大！网络加载、文件格式、运行环境隔离、支持第三方包、支持其他语言... 记录先到这里
