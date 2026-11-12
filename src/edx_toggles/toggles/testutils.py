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
        self._cached_value = None
        super().__init__(self.flag.name, active)

    def __enter__(self):
        super().__enter__()

        # Store values that have been cached on the flag
        self._cached_value = self.flag.cached_flags().get(self.name)
        self.flag.cached_flags()[self.name] = self.active

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)

        # Restore the cached values
        self.flag.cached_flags().pop(self.name, None)

        if self._cached_value is not None:
            self.flag.cached_flags()[self.name] = self._cached_value


class override_waffle_switch(override_switch):
    """
    Overrides the active value for the given switch for the duration of this
    contextmanager.
    Note: The value is overridden in the request cache AND in the model.

    Note: The implementation for overriding switches and flags differ. ``override_waffle_switch``
    makes an explicit call to ``WaffleSwitch.is_enabled``, which fills the cache, while
    ``override_waffle_flag`` only looks at the cached values. It is unclear whether this difference
    is important, or just due to being developed at different times by different people.
    """

    def __init__(self, switch, active):
        self.switch = switch
        self._previous_active = None
        super().__init__(switch.name, active)

    def __enter__(self):
        self._previous_active = self.switch.is_enabled()
        self.switch._cached_switches[self.switch.name] = self.active
        super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.switch._cached_switches[self.switch.name] = self._previous_active
