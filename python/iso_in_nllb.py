import argparse
import json

def load_language_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def find_related_languages(iso_code, language_data):
    # Find the language family of the given ISO code
    target_family = next((lang['languageFamily'] for lang in language_data if lang['isoCode'] == iso_code), None)
    
    if target_family is None:
        return []
    
    # Find all ISO codes in the same language family
    related_codes = [lang['isoCode'] for lang in language_data if lang['languageFamily'] == target_family and lang['isoCode'] != iso_code]
    
    return related_codes

def find_country_languages(iso_code, language_data):
    # Find the language family of the given ISO code
    target_country = next((lang['langCountry'] for lang in language_data if lang['isoCode'] == iso_code), None)
    
    if target_country is None:
        return []
    
    # Find all languages from that country
    country_codes = [lang['isoCode'] for lang in language_data if lang['langCountry'] == target_country and lang['isoCode'] != iso_code]
    
    return country_codes

def get_language_families(language_data):
    # Return a list of all the language families in the language data.
    return sorted(list(set(lang['languageFamily'] for lang in language_data)))
    

def main():
    parser = argparse.ArgumentParser(
        description="Return information about languages and whether they are known to NLLB."
    )
    parser.add_argument(
        "iso_codes", type=str, nargs="+", help="List of ISO codes to search for"
    )

    file_path = 'F:/GitHub/davidbaines/textinfo/languageFamilies.json'
    language_data = load_language_data(file_path)
    nllb_wses = ['ace_Arab', 'ace_Latn', 'acm_Arab', 'acq_Arab', 'aeb_Arab', 'afr_Latn', 'ajp_Arab', 'aka_Latn', 'amh_Ethi', 'apc_Arab', 'arb_Arab', 'ars_Arab', 'ary_Arab', 'arz_Arab', 'asm_Beng', 'ast_Latn', 'awa_Deva', 'ayr_Latn', 'azb_Arab', 'azj_Latn', 'bak_Cyrl', 'bam_Latn', 'ban_Latn', 'bel_Cyrl', 'bem_Latn', 'ben_Beng', 'bho_Deva', 'bjn_Arab', 'bjn_Latn', 'bod_Tibt', 'bos_Latn', 'bug_Latn', 'bul_Cyrl', 'cat_Latn', 'ceb_Latn', 'ces_Latn', 'cjk_Latn', 'ckb_Arab', 'crh_Latn', 'cym_Latn', 'dan_Latn', 'deu_Latn', 'dik_Latn', 'dyu_Latn', 'dzo_Tibt', 'ell_Grek', 'eng_Latn', 'epo_Latn', 'est_Latn', 'eus_Latn', 'ewe_Latn', 'fao_Latn', 'pes_Arab', 'fij_Latn', 'fin_Latn', 'fon_Latn', 'fra_Latn', 'fur_Latn', 'fuv_Latn', 'gla_Latn', 'gle_Latn', 'glg_Latn', 'grn_Latn', 'guj_Gujr', 'hat_Latn', 'hau_Latn', 'heb_Hebr', 'hin_Deva', 'hne_Deva', 'hrv_Latn', 'hun_Latn', 'hye_Armn', 'ibo_Latn', 'ilo_Latn', 'ind_Latn', 'isl_Latn', 'ita_Latn', 'jav_Latn', 'jpn_Jpan', 'kab_Latn', 'kac_Latn', 'kam_Latn', 'kan_Knda', 'kas_Arab', 'kas_Deva', 'kat_Geor', 'knc_Arab', 'knc_Latn', 'kaz_Cyrl', 'kbp_Latn', 'kea_Latn', 'khm_Khmr', 'kik_Latn', 'kin_Latn', 'kir_Cyrl', 'kmb_Latn', 'kon_Latn', 'kor_Hang', 'kmr_Latn', 'lao_Laoo', 'lvs_Latn', 'lij_Latn', 'lim_Latn', 'lin_Latn', 'lit_Latn', 'lmo_Latn', 'ltg_Latn', 'ltz_Latn', 'lua_Latn', 'lug_Latn', 'luo_Latn', 'lus_Latn', 'mag_Deva', 'mai_Deva', 'mal_Mlym', 'mar_Deva', 'min_Latn', 'mkd_Cyrl', 'plt_Latn', 'mlt_Latn', 'mni_Beng', 'khk_Cyrl', 'mos_Latn', 'mri_Latn', 'zsm_Latn', 'mya_Mymr', 'nld_Latn', 'nno_Latn', 'nob_Latn', 'npi_Deva', 'nso_Latn', 'nus_Latn', 'nya_Latn', 'oci_Latn', 'gaz_Latn', 'ory_Orya', 'pag_Latn', 'pan_Guru', 'pap_Latn', 'pol_Latn', 'por_Latn', 'prs_Arab', 'pbt_Arab', 'quy_Latn', 'ron_Latn', 'run_Latn', 'rus_Cyrl', 'sag_Latn', 'san_Deva', 'sat_Beng', 'scn_Latn', 'shn_Mymr', 'sin_Sinh', 'slk_Latn', 'slv_Latn', 'smo_Latn', 'sna_Latn', 'snd_Arab', 'som_Latn', 'sot_Latn', 'spa_Latn', 'als_Latn', 'srd_Latn', 'srp_Cyrl', 'ssw_Latn', 'sun_Latn', 'swe_Latn', 'swh_Latn', 'szl_Latn', 'tam_Taml', 'tat_Cyrl', 'tel_Telu', 'tgk_Cyrl', 'tgl_Latn', 'tha_Thai', 'tir_Ethi', 'taq_Latn', 'taq_Tfng', 'tpi_Latn', 'tsn_Latn', 'tso_Latn', 'tuk_Latn', 'tum_Latn', 'tur_Latn', 'twi_Latn', 'tzm_Tfng', 'uig_Arab', 'ukr_Cyrl', 'umb_Latn', 'urd_Arab', 'uzn_Latn', 'vec_Latn', 'vie_Latn', 'war_Latn', 'wol_Latn', 'xho_Latn', 'ydd_Hebr', 'yor_Latn', 'yue_Hant', 'zho_Hans', 'zho_Hant', 'zul_Latn']
    nllb_scripts = ['Arab', 'Armn', 'Beng', 'Cyrl', 'Deva', 'Ethi', 'Geor', 'Grek', 'Gujr', 'Guru', 'Hang', 'Hans', 'Hant', 'Hebr', 'Jpan', 'Khmr', 'Knda', 'Laoo', 'Latn', 'Mlym', 'Mymr', 'Orya', 'Sinh', 'Taml', 'Telu', 'Tfng', 'Thai', 'Tibt']
    nllb_isos = ['ace', 'acm', 'acq', 'aeb', 'afr', 'ajp', 'aka', 'als', 'amh', 'apc', 'arb', 'ars', 'ary', 'arz', 'asm', 'ast', 'awa', 'ayr', 'azb', 'azj', 'bak', 'bam', 'ban', 'bel', 'bem', 'ben', 'bho', 'bjn', 'bod', 'bos', 'bug', 'bul', 'cat', 'ceb', 'ces', 'cjk', 'ckb', 'crh', 'cym', 'dan', 'deu', 'dik', 'dyu', 'dzo', 'ell', 'eng', 'epo', 'est', 'eus', 'ewe', 'fao', 'fij', 'fin', 'fon', 'fra', 'fur', 'fuv', 'gaz', 'gla', 'gle', 'glg', 'grn', 'guj', 'hat', 'hau', 'heb', 'hin', 'hne', 'hrv', 'hun', 'hye', 'ibo', 'ilo', 'ind', 'isl', 'ita', 'jav', 'jpn', 'kab', 'kac', 'kam', 'kan', 'kas', 'kat', 'kaz', 'kbp', 'kea', 'khk', 'khm', 'kik', 'kin', 'kir', 'kmb', 'kmr', 'knc', 'kon', 'kor', 'lao', 'lij', 'lim', 'lin', 'lit', 'lmo', 'ltg', 'ltz', 'lua', 'lug', 'luo', 'lus', 'lvs', 'mag', 'mai', 'mal', 'mar', 'min', 'mkd', 'mlt', 'mni', 'mos', 'mri', 'mya', 'nld', 'nno', 'nob', 'npi', 'nso', 'nus', 'nya', 'oci', 'ory', 'pag', 'pan', 'pap', 'pbt', 'pes', 'plt', 'pol', 'por', 'prs', 'quy', 'ron', 'run', 'rus', 'sag', 'san', 'sat', 'scn', 'shn', 'sin', 'slk', 'slv', 'smo', 'sna', 'snd', 'som', 'sot', 'spa', 'srd', 'srp', 'ssw', 'sun', 'swe', 'swh', 'szl', 'tam', 'taq', 'tat', 'tel', 'tgk', 'tgl', 'tha', 'tir', 'tpi', 'tsn', 'tso', 'tuk', 'tum', 'tur', 'twi', 'tzm', 'uig', 'ukr', 'umb', 'urd', 'uzn', 'vec', 'vie', 'war', 'wol', 'xho', 'ydd', 'yor', 'yue', 'zho', 'zsm', 'zul']
    
    args = parser.parse_args()
    iso_codes = args.iso_codes
    for iso_code in iso_codes:

        related_languages = find_related_languages(iso_code, language_data)
        related_languages_in_nllb = [related_language for related_language in related_languages if related_language in nllb_isos]
        print(f"Found {len(related_languages_in_nllb)} Languages in the same family as {iso_code} that are known to NLLB:")
        print(related_languages_in_nllb)

if __name__ == "__main__":
    main()

# language_families= get_language_families(language_data)
# print(f"There are {len(language_families)} language families in the data")
# for language_familiy in language_families:
#     print(language_familiy)

#isos_to_find = ['ikx', 'nyp', 'teu', 'byt', 'zag', 'kbl', 'bms', 'kby', 'krt', 'knc', 'txj', 'dzg', 'tuq', 'dtn', 'guk', 'nrb', 'xnz', 'brk', 'dgl', 'ghl', 'kdu', 'drb', 'dil', 'elh', 'kko', 'wll', 'fia', 'mei', 'aft', 'nyi', 'mgb', 'sjg', 'tma', 'liu', 'shj', 'byg', 'djc', 'daj', 'dau', 'njl', 'soh', 'xel', 'zmo', 'tbi', 'bfa', 'keo', 'ukv', 'mqu', 'ddd', 'imt', 'lgo', 'lqr', 'lky', 'lpx', 'oie', 'lot', 'mas', 'nsg', 'saq', 'teo', 'kdj', 'nnj', 'toq', 'tuv', 'kpz', 'spy', 'sgc', 'enb', 'eyo', 'kqh', 'niq', 'tec', 'tuy', 'oki', 'pko', 'tcc', 'omt', 'dip', 'diw', 'dib', 'dks', 'dik', 'nus', 'atu', 'anu', 'bxb', 'lwo', 'bdi', 'jum', 'mfz', 'shk', 'thu', 'lkr', 'adh', 'kdi', 'lth', 'alz', 'ach', 'laj', 'luo', 'mpe', 'xwg', 'mym', 'muz', 'suq', 'did', 'loh', 'mur', 'tex', 'koe', 'teq', 'keg', 'kcp', 'xtc', 'kec', 'kgo', 'tey', 'tbr', 'gly', 'kmq', 'xom', 'lgn', 'udu', 'wti', 'led', 'dno', 'niy', 'asv', 'lmi', 'mdj', 'bct', 'efe', 'ndp', 'les', 'mdi', 'mdk', 'mxh', 'luc', 'avu', 'kbo', 'log', 'lgg', 'omi', 'mgd', 'mhi', 'snm', 'lul', 'blm', 'bdh', 'bot', 'bex', 'nwm', 'gbn', 'mgc', 'mwu', 'fuu', 'kcm', 'yul', 'bvq', 'fgr', 'bmi', 'bxv', 'dsi', 'glu', 'jyy', 'kyq', 'bdo', 'mne', 'bjv', 'dgk', 'gqr', 'gvl', 'hor', 'ksp', 'lap', 'mge', 'myb', 'nmc', 'sba', 'mwm', 'kwg', 'kwv', 'kxj', 'sbz', 'ndy', 'vae', 'sys', 'aja', 'krs', 'amj', 'fvr', 'kun', 'kth', 'klf', 'mde', 'mvu', 'mls', 'mdg', 'kie', 'rou', 'sbj', 'kcy', 'dsq', 'twq', 'ddn', 'hmb', 'khq', 'ses', 'tst', 'dje',]
# nllb_wses = ['ace_Arab', 'ace_Latn', 'acm_Arab', 'acq_Arab', 'aeb_Arab', 'afr_Latn', 'ajp_Arab', 'aka_Latn', 'amh_Ethi', 'apc_Arab', 'arb_Arab', 'ars_Arab', 'ary_Arab', 'arz_Arab', 'asm_Beng', 'ast_Latn', 'awa_Deva', 'ayr_Latn', 'azb_Arab', 'azj_Latn', 'bak_Cyrl', 'bam_Latn', 'ban_Latn', 'bel_Cyrl', 'bem_Latn', 'ben_Beng', 'bho_Deva', 'bjn_Arab', 'bjn_Latn', 'bod_Tibt', 'bos_Latn', 'bug_Latn', 'bul_Cyrl', 'cat_Latn', 'ceb_Latn', 'ces_Latn', 'cjk_Latn', 'ckb_Arab', 'crh_Latn', 'cym_Latn', 'dan_Latn', 'deu_Latn', 'dik_Latn', 'dyu_Latn', 'dzo_Tibt', 'ell_Grek', 'eng_Latn', 'epo_Latn', 'est_Latn', 'eus_Latn', 'ewe_Latn', 'fao_Latn', 'pes_Arab', 'fij_Latn', 'fin_Latn', 'fon_Latn', 'fra_Latn', 'fur_Latn', 'fuv_Latn', 'gla_Latn', 'gle_Latn', 'glg_Latn', 'grn_Latn', 'guj_Gujr', 'hat_Latn', 'hau_Latn', 'heb_Hebr', 'hin_Deva', 'hne_Deva', 'hrv_Latn', 'hun_Latn', 'hye_Armn', 'ibo_Latn', 'ilo_Latn', 'ind_Latn', 'isl_Latn', 'ita_Latn', 'jav_Latn', 'jpn_Jpan', 'kab_Latn', 'kac_Latn', 'kam_Latn', 'kan_Knda', 'kas_Arab', 'kas_Deva', 'kat_Geor', 'knc_Arab', 'knc_Latn', 'kaz_Cyrl', 'kbp_Latn', 'kea_Latn', 'khm_Khmr', 'kik_Latn', 'kin_Latn', 'kir_Cyrl', 'kmb_Latn', 'kon_Latn', 'kor_Hang', 'kmr_Latn', 'lao_Laoo', 'lvs_Latn', 'lij_Latn', 'lim_Latn', 'lin_Latn', 'lit_Latn', 'lmo_Latn', 'ltg_Latn', 'ltz_Latn', 'lua_Latn', 'lug_Latn', 'luo_Latn', 'lus_Latn', 'mag_Deva', 'mai_Deva', 'mal_Mlym', 'mar_Deva', 'min_Latn', 'mkd_Cyrl', 'plt_Latn', 'mlt_Latn', 'mni_Beng', 'khk_Cyrl', 'mos_Latn', 'mri_Latn', 'zsm_Latn', 'mya_Mymr', 'nld_Latn', 'nno_Latn', 'nob_Latn', 'npi_Deva', 'nso_Latn', 'nus_Latn', 'nya_Latn', 'oci_Latn', 'gaz_Latn', 'ory_Orya', 'pag_Latn', 'pan_Guru', 'pap_Latn', 'pol_Latn', 'por_Latn', 'prs_Arab', 'pbt_Arab', 'quy_Latn', 'ron_Latn', 'run_Latn', 'rus_Cyrl', 'sag_Latn', 'san_Deva', 'sat_Beng', 'scn_Latn', 'shn_Mymr', 'sin_Sinh', 'slk_Latn', 'slv_Latn', 'smo_Latn', 'sna_Latn', 'snd_Arab', 'som_Latn', 'sot_Latn', 'spa_Latn', 'als_Latn', 'srd_Latn', 'srp_Cyrl', 'ssw_Latn', 'sun_Latn', 'swe_Latn', 'swh_Latn', 'szl_Latn', 'tam_Taml', 'tat_Cyrl', 'tel_Telu', 'tgk_Cyrl', 'tgl_Latn', 'tha_Thai', 'tir_Ethi', 'taq_Latn', 'taq_Tfng', 'tpi_Latn', 'tsn_Latn', 'tso_Latn', 'tuk_Latn', 'tum_Latn', 'tur_Latn', 'twi_Latn', 'tzm_Tfng', 'uig_Arab', 'ukr_Cyrl', 'umb_Latn', 'urd_Arab', 'uzn_Latn', 'vec_Latn', 'vie_Latn', 'war_Latn', 'wol_Latn', 'xho_Latn', 'ydd_Hebr', 'yor_Latn', 'yue_Hant', 'zho_Hans', 'zho_Hant', 'zul_Latn']
# nllb_scripts = ['Arab', 'Armn', 'Beng', 'Cyrl', 'Deva', 'Ethi', 'Geor', 'Grek', 'Gujr', 'Guru', 'Hang', 'Hans', 'Hant', 'Hebr', 'Jpan', 'Khmr', 'Knda', 'Laoo', 'Latn', 'Mlym', 'Mymr', 'Orya', 'Sinh', 'Taml', 'Telu', 'Tfng', 'Thai', 'Tibt']
# nllb_isos = ['ace', 'acm', 'acq', 'aeb', 'afr', 'ajp', 'aka', 'als', 'amh', 'apc', 'arb', 'ars', 'ary', 'arz', 'asm', 'ast', 'awa', 'ayr', 'azb', 'azj', 'bak', 'bam', 'ban', 'bel', 'bem', 'ben', 'bho', 'bjn', 'bod', 'bos', 'bug', 'bul', 'cat', 'ceb', 'ces', 'cjk', 'ckb', 'crh', 'cym', 'dan', 'deu', 'dik', 'dyu', 'dzo', 'ell', 'eng', 'epo', 'est', 'eus', 'ewe', 'fao', 'fij', 'fin', 'fon', 'fra', 'fur', 'fuv', 'gaz', 'gla', 'gle', 'glg', 'grn', 'guj', 'hat', 'hau', 'heb', 'hin', 'hne', 'hrv', 'hun', 'hye', 'ibo', 'ilo', 'ind', 'isl', 'ita', 'jav', 'jpn', 'kab', 'kac', 'kam', 'kan', 'kas', 'kat', 'kaz', 'kbp', 'kea', 'khk', 'khm', 'kik', 'kin', 'kir', 'kmb', 'kmr', 'knc', 'kon', 'kor', 'lao', 'lij', 'lim', 'lin', 'lit', 'lmo', 'ltg', 'ltz', 'lua', 'lug', 'luo', 'lus', 'lvs', 'mag', 'mai', 'mal', 'mar', 'min', 'mkd', 'mlt', 'mni', 'mos', 'mri', 'mya', 'nld', 'nno', 'nob', 'npi', 'nso', 'nus', 'nya', 'oci', 'ory', 'pag', 'pan', 'pap', 'pbt', 'pes', 'plt', 'pol', 'por', 'prs', 'quy', 'ron', 'run', 'rus', 'sag', 'san', 'sat', 'scn', 'shn', 'sin', 'slk', 'slv', 'smo', 'sna', 'snd', 'som', 'sot', 'spa', 'srd', 'srp', 'ssw', 'sun', 'swe', 'swh', 'szl', 'tam', 'taq', 'tat', 'tel', 'tgk', 'tgl', 'tha', 'tir', 'tpi', 'tsn', 'tso', 'tuk', 'tum', 'tur', 'twi', 'tzm', 'uig', 'ukr', 'umb', 'urd', 'uzn', 'vec', 'vie', 'war', 'wol', 'xho', 'ydd', 'yor', 'yue', 'zho', 'zsm', 'zul']

# calc_isos = set([iso[:3] for iso in nllb_wses])

# print(f"calc_isos match nllb_isos : {calc_isos == set(nllb_isos)}")

# print(nllb_isos)
# print()
# print(calc_isos)


# isos_in_nllb = [iso for iso in isos if iso in nllb_isos]
# if isos_in_nllb:
#     print(f"These isos are in NLLB {isos_in_nllb}")
# else:
#     print(f"No isos in the list are known to NLLB")
