from funding_compiler.faculty_sources import faculty_sources_by_kind, load_faculty_sources


def test_load_uark_meeg_faculty_sources_includes_directory_and_tung():
    sources = load_faculty_sources("data/uark_meeg_faculty_sources.yaml")
    ids = {source.id for source in sources}

    assert "uark-meeg-faculty-directory" in ids
    assert "uark-meeg-steve-tung-profile" in ids


def test_load_uark_meeg_faculty_sources_includes_lab_sites_from_local_doc():
    sources = load_faculty_sources("data/uark_meeg_faculty_sources.yaml")
    labs = {source.name: source for source in sources if source.kind == "lab website"}

    assert labs["NED3 Lab"].owners == ["Han Hu"]
    assert labs["NED3 Lab"].url == "https://ned3.uark.edu/"
    assert labs["AM3 Lab"].owners == ["Wenchao Zhou"]


def test_faculty_sources_by_kind_groups_directory_and_labs():
    sources = load_faculty_sources("data/uark_meeg_faculty_sources.yaml")
    grouped = faculty_sources_by_kind(sources)

    assert "faculty directory" in grouped
    assert "lab website" in grouped
    assert len(grouped["lab website"]) >= 8
