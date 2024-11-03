# Node.js experiments

> Several experiments to see how Node.js executes JS codes and handles I/O events.

## Questions

1. The event loop of libuv uses OS-specific system calls (e.g. Linux: epoll, BSD: kqueue, Windows: IOCP) to handle pollable I/O events. However, these system calls themselves are blocking system calls! How can JS engine(in our case, V8) execute JS code without interfered by the blocking nature (caused by epoll, kqueue, or IOCP) of the event loop?

> The network socket based I/O events(caused by `fetch` API) are fired only when the evaluation of JS code is done. This means that even `connect` system call happens after all the JS code is evaluated. So whenever the CPU-intensive JS code is written below `fetch`, HTTP connection starts only after that JS code execution is done.

> You can check this behavior by running a local HTTP server and debugging [`./out/Debug/node one-fetch.js`](./one-fetch.js). Relavant breakpoints are listed below.
>
> 1. [A function for evaluating JS code with V8](/src/node_main_instance.cc#L107)
> 2. [A function for spinning the event loop](/src/node_main_instance.cc#L111)

2. How does libuv deals with timers? Does it uses separate threads, or checks if it is expired or not with timestamps (like how Linux kernel handles dynamic timers)? (Note that it seems the timer tick spins immediately when `setTimeout(cb, time)` is called, which means `cb` is called immediately when CPU-intensive code below `setTimeout` runs for more than `time`)

```js
setTimeout(() => console.log('timer done!'), 3000);
for (let i = 0; i < 1e10; i++) {}
console.log('timer start!');
```

> The timer mechanism used by libuv is timestamping. See [this link](https://stackoverflow.com/a/63714611) for more information. The following is extracted from the link.

> > Timer callbacks are executed as part of the NodeJS event loop. When you call `setTimeout` or `setInterval`, libuv (the C library which implements the NodeJS event loop) creates a timer in a 'min heap' data structure which is called the timers heap. In this data structure, it keeps track of the timestamp that each timer expires at.

> > At the start of each fresh iteration of the event loop, libuv calls `uv__update_time` which in turn calls a syscall to get the current time and updates the current loop time up to a millisecond precision. (https://github.com/nodejs/node/blob/master/deps/uv/src/unix/core.c#L375)

> > Right after that step comes the first major phase of the event loop iteration, which is timers phase. At this phase, libuv calls `uv__run_timers` to process all the callbacks of expired timers. During this phase, libuv traverses the timers heap to identify expired timers based on the 'loop time' it just updated using `uv__update_time`. Then it invokes the callbacks of all those expired timers.

> When Node.js spins the event loop, it is possible that the timer is already expired as there would be a JS code that takes long time below the call of `setTimeout`. This end up calling the callback of `setTimeout` right after the execution of JS code is done, not waiting for additional `time` milisecond we've specified as the second argument of `setTimeout`.

## How to check

Let's debug Node.js source code with gdb (or lldb)!

1. Compile Node.js with debug flags. (See [configure.py](/configure.py) for more information)

```console
./configure --ninja --debug --debug-node --debug-lib --debug-nghttp2 --v8-non-optimized-debug --v8-with-dchecks -C
make JOBS=4
```

2. Set breakpoints. The followings are several interesting lines you probably want to break.

   1. [A function for running main node instance](/src/node.cc#L1536)
   2. [A function for evaluating JS code with V8](/src/node_main_instance.cc#L107)
   3. [A function for JIT-compiling & executing JS code](/src/node_realm.cc#L161)
   4. [Right before jumping to JIT-compiled code](/deps/v8/src/execution/execution.cc#L418)
   5. [A function for spinning the event loop](/src/node_main_instance.cc#L111)
   6. [Right before running the event loop](/src/api/embed_helpers.cc#L41)

3. Debug with a debugger (in my case, CodeLLDB). Refer to [launch.json](/.vscode/launch.json) that I used.

## Notes

1. Unlike pollable I/O events like network sockets, regular file I/O inherently blocks the current thread. So libuv uses it's thread pool to handle this I/O events (Well, Linux can do asynchronous file I/O with `aio` or `io_uring`, but maybe this async file I/O is not a common feature that all the different kernels supports. I think the designer used this approach to make libuv highly portable.)

## Some good resources

https://blog.insiderattack.net/handling-io-nodejs-event-loop-part-4-418062f917d1

https://0xffffffff.tistory.com/99
