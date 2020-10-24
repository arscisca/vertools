import vertools
import vertools.context as vcontext

import pytest

def test_scope():
    # Test reading
    scope = vcontext.Scope.from_config(vertools.rootdir/'test/files/example_base.config')
    assert scope.get('Section 1', 'x') == '1'
    assert scope.get('Section 1', 'y') == "multi\nline\nvalue"
    assert scope.get('Section 2', 'z') == '1 ns'
    # Test error
    with pytest.raises(vcontext.Scope.NoSectionError):
        x = scope.get('Nonexisting section', 'x')
    with pytest.raises(vcontext.Scope.NoParameterError):
        nonexisting_parameter = scope.get('Section 1', 'nonexisting_parameter')


def test_context():
    context = vcontext.Context()
    global_scope = vcontext.Scope.from_config(vertools.rootdir/'test/files/example_base.config')
    local_scope = vcontext.Scope.from_config(vertools.rootdir/'test/files/example_override.config')
    context.append_local(global_scope)
    context.append_local(local_scope)
    # Test relationships
    assert context.most_global() is global_scope
    assert context.most_local() is local_scope
    assert context.most_global().upper is local_scope
    assert context.most_local().lower is global_scope
    # Test lookup
    assert context.get('Section 1', 'x') == 'x was correctly overridden'
    assert context.get('Section 1', 'y') == "multi\nline\nvalue"
    assert context.get('Section 2', 'z') == '1 ns'
    assert context.get('New section', 'new') == 'new parameter now exists'
    # Test error
    with pytest.raises(vcontext.Context.LookupError):
        x = context.get('Nonexisting section', 'x')
    with pytest.raises(vcontext.Context.LookupError):
        nonexisting_parameter = context.get('Section 1', 'nonexisting_parameter')
