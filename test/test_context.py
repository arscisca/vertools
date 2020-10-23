import vertools
import vertools.context as vcontext


def test_context():
    # Test reading
    lower = vcontext.Context.from_config(vertools.rootdir/'test/files/example_base.config')
    assert lower.get('Section 1', 'x') == '1'
    assert lower.get('Section 1', 'y') == "multi\nline\nvalue"
    assert lower.get('Section 2', 'z') == '1 ns'

    # Test overriding
    upper = vcontext.Context.from_config(vertools.rootdir/'test/files/example_override.config')
    upper.override(lower)
    assert upper.get('Section 1', 'x') == 'x was correctly overridden'
    assert upper.get('Section 1', 'y') == "multi\nline\nvalue"
    assert upper.get('Section 2', 'z') == '1 ns'
    assert upper.get('New section', 'new') == 'new parameter now exists'

    # Test relations
    assert lower.top_level() is upper
    assert lower.bottom_level() is lower
    assert upper.top_level() is upper
    assert upper.bottom_level() is lower
