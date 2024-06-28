import argparse
import json


def load_language_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        raw_data = json.load(file)

    # Restructure the data for faster lookups
    language_data = {}
    country_data = {}
    family_data = {}

    for lang in raw_data:
        iso = lang["isoCode"]
        country = lang["langCountry"]
        family = lang["languageFamily"]

        language_data[iso] = {
            "Name": lang["language"],
            "Country": country,
            "Family": family,
        }

        country_data.setdefault(country, []).append(iso)
        family_data.setdefault(family, []).append(iso)

    return language_data, country_data, family_data


def process_iso_codes(iso_codes, language_data, country_data, family_data, nllb_isos):
    iso_set = set(iso_codes)

    for iso in iso_codes:
        if iso in language_data:
            lang_info = language_data[iso]
            print(
                f"{iso}: {lang_info['Name']}, {lang_info['Country']}, {lang_info['Family']}"
            )

            # Add iso codes from the same country
            iso_set.update(country_data.get(lang_info["Country"], []))

            # Add iso codes from the same family
            iso_set.update(family_data.get(lang_info["Family"], []))

    # Remove iso codes not in NLLB
    nllb_set = set(nllb_isos)
    iso_set_in_nllb = iso_set.intersection(nllb_set)

    print("\nISO codes in the overall set that are in NLLB:")
    print(sorted(iso_set_in_nllb))


def main():
    parser = argparse.ArgumentParser(
        description="Process language data and find related languages in NLLB."
    )
    parser.add_argument(
        "iso_codes", type=str, nargs="+", help="List of ISO codes to process"
    )

    args = parser.parse_args()
    iso_codes = args.iso_codes

    file_path = "F:/GitHub/davidbaines/textinfo/languageFamilies.json"
    language_data, country_data, family_data = load_language_data(file_path)

    nllb_isos = [
        "ace",
        "acm",
        "acq",
        "aeb",
        "afr",
        "ajp",
        "aka",
        "als",
        "amh",
        "apc",
        "arb",
        "ars",
        "ary",
        "arz",
        "asm",
        "ast",
        "awa",
        "ayr",
        "azb",
        "azj",
        "bak",
        "bam",
        "ban",
        "bel",
        "bem",
        "ben",
        "bho",
        "bjn",
        "bod",
        "bos",
        "bug",
        "bul",
        "cat",
        "ceb",
        "ces",
        "cjk",
        "ckb",
        "crh",
        "cym",
        "dan",
        "deu",
        "dik",
        "dyu",
        "dzo",
        "ell",
        "eng",
        "epo",
        "est",
        "eus",
        "ewe",
        "fao",
        "fij",
        "fin",
        "fon",
        "fra",
        "fur",
        "fuv",
        "gaz",
        "gla",
        "gle",
        "glg",
        "grn",
        "guj",
        "hat",
        "hau",
        "heb",
        "hin",
        "hne",
        "hrv",
        "hun",
        "hye",
        "ibo",
        "ilo",
        "ind",
        "isl",
        "ita",
        "jav",
        "jpn",
        "kab",
        "kac",
        "kam",
        "kan",
        "kas",
        "kat",
        "kaz",
        "kbp",
        "kea",
        "khk",
        "khm",
        "kik",
        "kin",
        "kir",
        "kmb",
        "kmr",
        "knc",
        "kon",
        "kor",
        "lao",
        "lij",
        "lim",
        "lin",
        "lit",
        "lmo",
        "ltg",
        "ltz",
        "lua",
        "lug",
        "luo",
        "lus",
        "lvs",
        "mag",
        "mai",
        "mal",
        "mar",
        "min",
        "mkd",
        "mlt",
        "mni",
        "mos",
        "mri",
        "mya",
        "nld",
        "nno",
        "nob",
        "npi",
        "nso",
        "nus",
        "nya",
        "oci",
        "ory",
        "pag",
        "pan",
        "pap",
        "pbt",
        "pes",
        "plt",
        "pol",
        "por",
        "prs",
        "quy",
        "ron",
        "run",
        "rus",
        "sag",
        "san",
        "sat",
        "scn",
        "shn",
        "sin",
        "slk",
        "slv",
        "smo",
        "sna",
        "snd",
        "som",
        "sot",
        "spa",
        "srd",
        "srp",
        "ssw",
        "sun",
        "swe",
        "swh",
        "szl",
        "tam",
        "taq",
        "tat",
        "tel",
        "tgk",
        "tgl",
        "tha",
        "tir",
        "tpi",
        "tsn",
        "tso",
        "tuk",
        "tum",
        "tur",
        "twi",
        "tzm",
        "uig",
        "ukr",
        "umb",
        "urd",
        "uzn",
        "vec",
        "vie",
        "war",
        "wol",
        "xho",
        "ydd",
        "yor",
        "yue",
        "zho",
        "zsm",
        "zul",
    ]

    process_iso_codes(iso_codes, language_data, country_data, family_data, nllb_isos)


if __name__ == "__main__":
    main()
