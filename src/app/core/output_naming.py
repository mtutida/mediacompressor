
import os
import datetime
from app.ancillary.configuration import ConfigurationService

def generate_output_path(input_path):
    cfg = ConfigurationService.instance().get()

    base_dir = os.path.dirname(input_path)
    name, ext = os.path.splitext(os.path.basename(input_path))

    # directory
    if getattr(cfg, "use_source_directory", True):
        directory = base_dir
    else:
        directory = cfg.output_directory or base_dir

    # naming mode
    mode = getattr(cfg, "output_naming_mode", 0)

    if mode == 0:
        output_name = name + ext

    elif mode == 1:
        suffix = getattr(cfg, "output_suffix", "").strip()

        if "|" in suffix:
            suffix = suffix.split("|")[0].strip()

        # fallback if user left suffix empty
        if not suffix:
            suffix = "_compactado"

        if not suffix.startswith("_"):
            suffix = "_" + suffix

        output_name = name + suffix + ext

    elif mode == 2:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        output_name = f"{name}_{ts}{ext}"

    output = os.path.join(directory, output_name)

    # collision policy
    policy = getattr(cfg, "collision_policy", 0)

    if policy == 0:  # sequential numbering
        counter = 1
        base_output = output
        while os.path.exists(output):
            name2, ext2 = os.path.splitext(base_output)
            output = f"{name2}_{counter}{ext2}"
            counter += 1

    elif policy == 1:  # overwrite
        pass

    elif policy == 2:  # cancel
        if os.path.exists(output):
            raise Exception("Arquivo de saída já existe")

    return output
