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
        lst = sort_strings([i for i in os.listdir(name + "_files") if "png" in i])
        lst = [
            "https://github.com/MaceKuailv/seaduck_sciserver_notebook/blob/master/"
            + name
            + "_files/"
            + i
            + "?raw=true"
            for i in lst
        ]

        insert_png_line(name + ".md", lst)
        insert_date(name + ".md")
#        just_markdown(name+'.md')
