def test_sub_extraction():
    from parse.lotus_regex_fallback import extract_subs_from_text
    txt = "Sub Foo()\n x=1\nEnd Sub\n"
    subs = extract_subs_from_text(txt)
    assert len(subs) == 1
    assert "Sub Foo" in subs[0]
