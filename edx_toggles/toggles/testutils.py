"""
Toggle test utilities.
"""
from waffle.testutils import override_flag, override_switch


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
        super().__init__(name, active)

    def __enter__(self):
        super().__enter__()

        # Store values that have been cached on the flag
        self._cached_value = self.flag.waffle_namespace._cached_flags.get(self.name)
        self.flag.waffle_namespace._cached_flags[self.name] = self.active

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)

        # Restore the cached values
        waffle_namespace = self.flag.waffle_namespace
        waffle_namespace._cached_flags.pop(self.name, None)

        if self._cached_value is not None:
            waffle_namespace._cached_flags[self.name] = self._cached_value


class override_waffle_switch(override_switch):
    """
    Overrides the active value for the given switch for the duration of this
    contextmanager.
    Note: The value is overridden in the request cache AND in the model.
    """

    def __init__(self, switch, active):
        self.switch = switch
        self._cached_value = None
        self._previous_active = None
        super().__init__(switch.namespaced_switch_name, active)

    def __enter__(self):
        self._previous_active = self.switch.waffle_namespace.is_enabled(
            self.switch.switch_name
        )
        self.switch.waffle_namespace.set_request_cache(self.switch.namespaced_switch_name, self.active)
        super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.switch.waffle_namespace.set_request_cache(self.switch.namespaced_switch_name, self._previous_active)
