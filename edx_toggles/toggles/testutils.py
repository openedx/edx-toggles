"""
Toggle test utilities.
"""
from waffle.testutils import override_flag


class override_waffle_flag(override_flag):
    """
    override_waffle_flag is a contextmanager for easier testing of flags.

    It accepts two parameters, the flag itself and its intended state. Example
    usage::

        with override_waffle_flag(SOME_COURSE_FLAG, active=True):
            ...

    If the flag already exists, its value will be changed inside the context
    block, then restored to the original value. If the flag does not exist
    before entering the context, it is created, then removed at the end of the
    block.

    It can also act as a decorator::

        @override_waffle_flag(SOME_COURSE_FLAG, active=True)
        def test_happy_mode_enabled():
            ...
    """

    def __init__(self, flag, active):
        """

        Args:
             flag (WaffleFlag): The namespaced cached waffle flag.
             active (Boolean): The value to which the flag will be set.
        """
        self.flag = flag
        waffle_namespace = flag.waffle_namespace
        name = waffle_namespace._namespaced_name(flag.flag_name)
        self._cached_value = None
        super(override_waffle_flag, self).__init__(name, active)

    def __enter__(self):
        super(override_waffle_flag, self).__enter__()

        # Store values that have been cached on the flag
        self._cached_value = self.flag.waffle_namespace._cached_flags.get(self.name)
        self.flag.waffle_namespace._cached_flags[self.name] = self.active

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(override_waffle_flag, self).__exit__(exc_type, exc_val, exc_tb)

        # Restore the cached values
        waffle_namespace = self.flag.waffle_namespace
        waffle_namespace._cached_flags.pop(self.name, None)

        if self._cached_value is not None:
            waffle_namespace._cached_flags[self.name] = self._cached_value
