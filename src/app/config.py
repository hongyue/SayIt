VOICES = {
    "US English": {
        "lang_code": "a",
        "voices": [
            {"name": "af_heart", "label": "Heart", "gender": "female"},
            {"name": "af_alloy", "label": "Alloy", "gender": "female"},
            {"name": "af_aoede", "label": "Aoede", "gender": "female"},
            {"name": "af_bella", "label": "Bella", "gender": "female"},
            {"name": "af_jessica", "label": "Jessica", "gender": "female"},
            {"name": "af_kore", "label": "Kore", "gender": "female"},
            {"name": "af_nicole", "label": "Nicole", "gender": "female"},
            {"name": "af_nova", "label": "Nova", "gender": "female"},
            {"name": "af_river", "label": "River", "gender": "female"},
            {"name": "af_sarah", "label": "Sarah", "gender": "female"},
            {"name": "af_sky", "label": "Sky", "gender": "female"},
            {"name": "am_adam", "label": "Adam", "gender": "male"},
            {"name": "am_echo", "label": "Echo", "gender": "male"},
            {"name": "am_eric", "label": "Eric", "gender": "male"},
            {"name": "am_fenrir", "label": "Fenrir", "gender": "male"},
            {"name": "am_liam", "label": "Liam", "gender": "male"},
            {"name": "am_michael", "label": "Michael", "gender": "male"},
            {"name": "am_onyx", "label": "Onyx", "gender": "male"},
            {"name": "am_puck", "label": "Puck", "gender": "male"},
            {"name": "am_santa", "label": "Santa", "gender": "male"},
        ],
    },
    "UK English": {
        "lang_code": "b",
        "voices": [
            {"name": "bf_alice", "label": "Alice", "gender": "female"},
            {"name": "bf_emma", "label": "Emma", "gender": "female"},
            {"name": "bf_isabella", "label": "Isabella", "gender": "female"},
            {"name": "bf_lily", "label": "Lily", "gender": "female"},
            {"name": "bm_daniel", "label": "Daniel", "gender": "male"},
            {"name": "bm_fable", "label": "Fable", "gender": "male"},
            {"name": "bm_george", "label": "George", "gender": "male"},
            {"name": "bm_lewis", "label": "Lewis", "gender": "male"},
        ],
    },
    "Japanese": {
        "lang_code": "j",
        "voices": [
            {"name": "jf_alpha", "label": "Alpha", "gender": "female"},
            {"name": "jf_gongitsune", "label": "Gongitsune", "gender": "female"},
            {"name": "jf_nezumi", "label": "Nezumi", "gender": "female"},
            {"name": "jf_tebukuro", "label": "Tebukuro", "gender": "female"},
            {"name": "jm_kumo", "label": "Kumo", "gender": "male"},
        ],
    },
    "Mandarin Chinese": {
        "lang_code": "z",
        "voices": [
            {"name": "zf_xiaobei", "label": "Xiaobei", "gender": "female"},
            {"name": "zf_xiaoni", "label": "Xiaoni", "gender": "female"},
            {"name": "zf_xiaoxiao", "label": "Xiaoxiao", "gender": "female"},
            {"name": "zf_xiaoyi", "label": "Xiaoyi", "gender": "female"},
            {"name": "zm_yunjian", "label": "Yunjian", "gender": "male"},
            {"name": "zm_yunxi", "label": "Yunxi", "gender": "male"},
            {"name": "zm_yunxia", "label": "Yunxia", "gender": "male"},
            {"name": "zm_yunyang", "label": "Yunyang", "gender": "male"},
        ],
    },
    "Spanish": {
        "lang_code": "e",
        "voices": [
            {"name": "ef_dora", "label": "Dora", "gender": "female"},
            {"name": "em_alex", "label": "Alex", "gender": "male"},
            {"name": "em_santa", "label": "Santa", "gender": "male"},
        ],
    },
    "French": {
        "lang_code": "f",
        "voices": [
            {"name": "ff_siwis", "label": "Siwis", "gender": "female"},
        ],
    },
    "Hindi": {
        "lang_code": "h",
        "voices": [
            {"name": "hf_alpha", "label": "Alpha", "gender": "female"},
            {"name": "hf_beta", "label": "Beta", "gender": "female"},
            {"name": "hm_omega", "label": "Omega", "gender": "male"},
            {"name": "hm_psi", "label": "Psi", "gender": "male"},
        ],
    },
    "Italian": {
        "lang_code": "i",
        "voices": [
            {"name": "if_sara", "label": "Sara", "gender": "female"},
            {"name": "im_nicola", "label": "Nicola", "gender": "male"},
        ],
    },
    "Brazilian Portuguese": {
        "lang_code": "p",
        "voices": [
            {"name": "pf_dora", "label": "Dora", "gender": "female"},
            {"name": "pm_alex", "label": "Alex", "gender": "male"},
            {"name": "pm_santa", "label": "Santa", "gender": "male"},
        ],
    },
}

VOICE_LANG_MAP = {}
for lang, data in VOICES.items():
    for voice in data["voices"]:
        VOICE_LANG_MAP[voice["name"]] = data["lang_code"]

CHUNK_SIZE = 2000
SAMPLE_RATE = 24000
