import os
import stat
import shutil
import json

# LOGGING METHODS
def log(message, code):
    code_str = f"[ {code.upper()} ]".ljust(10)
    print('{}{}'.format(code_str, message))

def logmsg(message):
    log(message, 'INFO')

def logwarn(message):
    log(message, 'WARN')

def logerr(message):
    global error_count
    log(message, 'ERROR')
    error_count += 1


# EXIT AND FAILURE METHODS
def exit_failure():
    log("Failed to Build Project, Exiting...", "EXIT")
    log("Found {} Errors".format(error_count), "EXIT")
    exit(1)

def check_failure():
    if error_count:
        exit_failure()

error_count = 0


# COPYING METHOD
def copy_directory(wd, src, dst):
    files = [os.path.join(src, f) for f in os.listdir(src) if os.path.isfile(os.path.join(src, f)) and f.endswith('.py')]
    for f in files:
        try:
            rel_path = os.path.relpath(f, wd)
            destination = os.path.join(dst, rel_path)
            if not os.path.exists(os.path.dirname(destination)):
                os.makedirs(os.path.dirname(destination))
            shutil.copy(f, destination)
        except shutil.Error as e:
            logerr("Failed to copy {}: {}".format(f, str(e)))
        except Exception as e:
            logerr("Unknown Error: " + str(e))



def main():
    global error_count

    # PREP PHASE
    # read the build settings from json "build-settings.json"
    build_settings: dict = {}
    try:
        build_settings = json.load(open("build-settings.json"))
    except FileNotFoundError:
        logerr("File Not Found: build-settings.json!")
    except json.decoder.JSONDecodeError:
        logerr("Invalid JSON: build-settings.json!")
    except Exception as e:
        logerr("Unknown Exception: " + str(e))

    check_failure()

    # prepare variables for the build phase
    # these are read from the JSON
    build_dir: str
    source_dir: str

    try:
        work_dir = os.path.expanduser(build_settings['work-dir'])
        build_dir = str(os.path.join(work_dir, build_settings['build-dir']))
        source_dir = str(os.path.join(work_dir, build_settings['source-dir']))
    except KeyError as e:
        logerr("Key Not Found: " + str(e))
    except Exception as e:
        logerr("Unknown Exception: " + str(e))

    logmsg("Working Directory: {}".format(work_dir))
    logmsg("Build Directory: {}".format(build_dir))
    logmsg("Source Directory: {}".format(source_dir))

    check_failure()

    # BUILD PHASE
    if not build_settings.get('keep-original-structure'):
        logmsg("Overriding Original File Structure")
        logmsg("Copying Source Files")
        try:
            shutil.copytree(source_dir, build_dir, dirs_exist_ok=True)
        except shutil.Error as e:
            logerr("Failed to copy source files: " + str(e))
        except Exception as e:
            logerr("Unknown Exception: " + str(e))

        logmsg("Copying Miscellaneous Files")
        for file in build_settings.get('misc-include'):
            try:
                shutil.copy(str(os.path.join(work_dir, file)), build_dir)
            except shutil.Error as e:
                logerr("Failed to copy file: " + str(e))
            except Exception as e:
                logerr("Unknown Exception: " + str(e))

        check_failure()


    else:
        logmsg("Keeping Original File Structure")
        logmsg("Copying Source Files")
        try:
            copy_directory(work_dir, source_dir, build_dir)
        except shutil.Error as e:
            logerr("Failed to copy source files: " + str(e))
        except Exception as e:
            logerr("Unknown Exception: " + str(e))

        logmsg("Copying Miscellaneous Files")
        for file in build_settings.get('misc-include'):
            logmsg("Copying {}".format(file))
            try:
                file_dir = os.path.dirname(file)
                shutil.copy(str(os.path.join(work_dir, file)), str(os.path.join(build_dir, str(file_dir))))
            except shutil.Error as e:
                logerr("Failed to copy file: " + str(e))
            except Exception as e:
                logerr("Unknown Exception: " + str(e))

        check_failure()



    if build_settings.get('create-executable') and build_settings.get('program-entry'):
        executable_path = os.path.join(build_dir, 'Executable')
        logmsg("Creating executable: {}".format(executable_path))

        entry = build_settings['program-entry']
        entry_path: str
        if build_settings.get('keep-original-structure'):
            entry_path = os.path.join(build_dir, os.path.relpath(source_dir, work_dir), entry)
        else:
            entry_path = os.path.join(build_dir, entry)
        logmsg("Entry Path set to {}".format(entry_path))
        try:
            with open(executable_path, 'w', newline='\n') as f:
                f.write("#!/bin/bash")
                f.write("\n")
                f.write('python3 "{}"'.format(entry_path))

            os.chmod(executable_path, os.stat(executable_path).st_mode | stat.S_IXUSR)
        except PermissionError as e:
            logwarn("Failed to create executable: " + str(e))
        except Exception as e:
            logerr("Failed to create executable: " + str(e))

        logmsg("Finished Creating Executable")

    check_failure()



    log("Finished Building Project!", "done")



if __name__ == "__main__":
    main()