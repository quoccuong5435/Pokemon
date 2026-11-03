import jasscheck

KNOWN = {'DestroyEffect': 1, 'AddSpecialEffectTarget': 3, 'GetTriggerUnit': 0}


def check(src, globals_=()):
    return jasscheck.check(src, KNOWN, set(globals_))


OK = '''
globals
    integer Mega_X = 0
    unit array Mega_U
endglobals
function Mega_A takes unit u, integer n returns integer
    local effect e = AddSpecialEffectTarget("x.mdl", u, "origin")
    local integer i = 0
    loop
        exitwhen i >= n
        set Mega_U[i] = u
        set i = i + 1
    endloop
    if n > 1 then
        call DestroyEffect(e)
    elseif n == 1 then
        set Mega_X = 'hM00'
    else
        return 0
    endif
    return i
endfunction
function Mega_B takes nothing returns nothing
    call Mega_A(GetTriggerUnit(), 2) // comment with ( "
endfunction
'''


def test_ok_snippet():
    assert check(OK) == []


def test_unknown_function():
    errs = check('function Mega_A takes nothing returns nothing\n    call Foo()\nendfunction\n')
    assert any('Foo' in e for e in errs)


def test_wrong_arg_count():
    errs = check('function Mega_A takes effect a returns nothing\n    call DestroyEffect(a, a)\nendfunction\n')
    assert any('DestroyEffect' in e and 'argument' in e for e in errs)


def test_unbalanced_if():
    errs = check('function Mega_A takes nothing returns nothing\n    if true then\n    call GetTriggerUnit()\n'
                 'endfunction\n')
    assert any('endif' in e or 'if' in e for e in errs)


def test_undeclared_variable():
    errs = check('function Mega_A takes nothing returns nothing\n    set Mega_Y = 1\nendfunction\n')
    assert any('Mega_Y' in e for e in errs)


def test_call_before_definition():
    errs = check('function Mega_A takes nothing returns nothing\n    call Mega_B()\nendfunction\n'
                 'function Mega_B takes nothing returns nothing\nendfunction\n')
    assert any('Mega_B' in e for e in errs)


def test_local_after_statement():
    errs = check('function Mega_A takes nothing returns nothing\n    call GetTriggerUnit()\n'
                 '    local integer i = 0\nendfunction\n')
    assert any('local' in e for e in errs)


def test_known_global_ok():
    src = 'function Mega_A takes nothing returns nothing\n    call DestroyEffect(SOME_CONST)\nendfunction\n'
    assert check(src, ['SOME_CONST']) == []


def test_code_reference_checked():
    errs = check('function Mega_A takes nothing returns nothing\n    call DestroyEffect(function Mega_Z)\n'
                 'endfunction\n')
    assert any('Mega_Z' in e for e in errs)
