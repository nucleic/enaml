# ------------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
import asyncio
import os
import sys
from inspect import iscoroutine
from queue import Empty, Queue

import enaml
from atom.api import Bool, Typed
from enaml.qt.qt_application import QtApplication

try:
    from asyncqtpy import QEventLoopPolicy
except ImportError:
    try:
        from qasync import DefaultQEventLoopPolicy as QEventLoopPolicy
    except ImportError:
        print("Please install 'asyncqtpy' or 'qasync'")
        sys.exit(1)


sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class AsyncQtApplication(QtApplication):
    queue = Typed(Queue, ())
    running = Bool()

    def start(self):
        try:
            self.running = True
            loop = asyncio.new_event_loop()
            with loop:
                loop.run_until_complete(self.main())
            super().stop()
        except RuntimeError:
            pass  # Loop stopped
        finally:
            self.running = False

    async def main(self):
        """Run any async deferred calls in the main ui loop."""
        while self.running:
            try:
                await self.queue.get(block=False)
            except Empty:
                await asyncio.sleep(0.1)
            except Exception as e:
                # Handle errors here
                raise e

    def stop(self):
        self.running = False

    def deferred_call(self, callback, *args, **kwargs):
        if iscoroutine(callback):
            return self.queue.put(callback)
        return super().deferred_call(callback, *args, **kwargs)

    def timed_call(self, ms, callback, *args, **kwargs):
        if iscoroutine(callback):
            return super().timed_call(ms, self.queue.put, callback)
        return super().timed_call(callback, *args, **kwargs)


def main():
    asyncio.set_event_loop_policy(QEventLoopPolicy())

    with enaml.imports():
        from async_view import Main

    app = AsyncQtApplication()

    view = Main()
    view.show()

    # Start the application event loop
    app.start()


if __name__ == "__main__":
    main()
