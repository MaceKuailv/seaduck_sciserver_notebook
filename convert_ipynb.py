import subprocess
import os
import datetime
import seaduck as sd
import re


def test_notebook(nbname, execute=False):
    if execute:
        result = subprocess.call(
            ["jupyter", "nbconvert", "--to", "markdown", "--execute", nbname]
        )
    else:
        result = subprocess.call(["jupyter", "nbconvert", "--to", "markdown", nbname])
    if result != 0:
        raise Exception("The notebook failed, my friend")


def to_myst(nbname):
    result = subprocess.call(["jupytext", "--to", "myst", nbname])
    if result != 0:
        raise Exception("MYST failed")


def remove_kernelspec(mdname):
    """Remove kernelspec metadata from MyST markdown file.

    The markdown files are static documentation (pre-rendered) and should not
    be executed by mystmd. Removing kernelspec prevents mystmd from trying to
    execute them with the (non-existent) oceanography kernel.
    """
    with open(mdname, "r") as file:
        lines = file.readlines()

    # Find and remove kernelspec section while keeping jupytext metadata
    new_lines = []
    skip_kernelspec = False
    for i, line in enumerate(lines):
        if line.startswith("kernelspec:"):
            skip_kernelspec = True
            continue
        if skip_kernelspec:
            # Skip until we find the next section (starts with non-space or end of metadata)
            if line.startswith("---") or (line.strip() and not line[0].isspace()):
                skip_kernelspec = False
                if line.startswith("---"):
                    new_lines.append(line)
                    continue
            else:
                continue
        new_lines.append(line)

    with open(mdname, "w") as file:
        file.writelines(new_lines)


def sort_strings(strings):
    def extract_numbers(string):
        # Extract numbers using regular expression pattern
        numbers = re.findall(r"\d+", string)
        return [int(num) for num in numbers]

    def string_sort_key(string):
        # Split the string into parts using underscores
        parts = string.split("_")
        # Extract the numbers from the relevant parts
        numbers = extract_numbers("_".join(parts[1:]))
        return parts[0], numbers

    sorted_strings = sorted(strings, key=string_sort_key)
    return sorted_strings


def insert_png_line(filename, photos):
    with open(filename, "r") as file:
        lines = file.readlines()

    # Find the line containing "plt.show()"
    show_line_index = []
    for i, line in enumerate(lines):
        if "plt.show()" in line:
            show_line_index.append(i)
    if len(photos) != len(show_line_index):
        raise Exception(
            f"photo{len(photos)} and plt.show{len(show_line_index)}"
            " not the same number. "
            ""
        )
    cum = 0
    for il, line in enumerate(show_line_index):
        # Insert the new line two lines after "plt.show()"
        png_line = f"![png]({photos[il]})\n"
        lines.insert(line + 2 + cum, png_line)
        cum += 1

    with open(filename, "w") as file:
        file.writelines(lines)


def insert_date(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    show_line_index = None
    for i, line in enumerate(lines):
        if "Wenrui Jiang" in line:
            show_line_index = i
            break
    if show_line_index is None:
        raise Exception("This notebook is not by wenrui jiang, I dont know what to do")
    current_date = datetime.date.today()
    today = f"> **Warning**⚠️ : the notebook was last ran on **{current_date}** "
    version = f"with **seaduck {sd.__version__}**. "
    url = (
        "https://github.com/MaceKuailv/seaduck_sciserver_notebook/blob/master/"
        + filename[:-3]
        + ".ipynb"
    )
    where2find = f"You can find the executable version at {url}. "
    # warning_block = [
    # '<div class="alert alert-block alert-warning">',
    # '<b>Download:</b>'+today,
    # '</div>'
    # ]

    lines.insert(show_line_index + 1, today + version + where2find)
    # lines[show_line_index + 1:show_line_index + 1] = warning_block
    with open(filename, "w") as file:
        file.writelines(lines)


def just_markdown(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
    for i, lin in enumerate(lines):
        if "#" in lin:
            break
    lines = lines[i:]
    with open(filename, "w") as file:
        file.writelines(lines)


if __name__ == "__main__":
    notebook_names = [
        "IGPwinter.ipynb",
        "LLC4320.ipynb",
        "KangerFjord.ipynb",
        "ECCO_plot_stations.ipynb",
    ]
    # notebook_names = [i for i in os.listdir(".") if ".ipynb" in i]
    for nbname in notebook_names:
        print(nbname)
        test_notebook(nbname)
        to_myst(nbname)

        name = nbname[:-6]
        md_name = name + ".md"

        # Remove kernelspec metadata (MyST v2 compatibility)
        remove_kernelspec(md_name)

        lst = sort_strings([i for i in os.listdir(name + "_files") if "png" in i])
        lst = [
            "https://github.com/MaceKuailv/seaduck_sciserver_notebook/blob/master/"
            + name
            + "_files/"
            + i
            + "?raw=true"
            for i in lst
        ]

        insert_png_line(md_name, lst)
        insert_date(md_name)
#        just_markdown(name+'.md')
