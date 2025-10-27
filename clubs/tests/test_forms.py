from clubs.forms import ClubPostForm

def test_clubpost_form_invalid():
    form = ClubPostForm(data={})
    assert not form.is_valid()