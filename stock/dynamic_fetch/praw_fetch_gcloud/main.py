import os
import subprocess
import mongo_setup

def download_spacy_model():
    try:
        import en_core_web_sm
    except ImportError:
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
        import en_core_web_sm

def entry_point(request):
    download_spacy_model()
    mongo_setup.main()
    return 'Function executed successfully', 200

if __name__ == "__main__":
    download_spacy_model()
    mongo_setup.main()
