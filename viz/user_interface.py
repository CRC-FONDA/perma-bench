"""
    This module creates HTML pages for each benchmark with index.html as an entry point to the user interface.
"""

import dominate
import glob
import os
import shutil
import raw_json_reader as raw_reader

from collections import defaultdict
from dominate import tags


def new_html_page(benchmark_pngs):
    doc = dominate.document(title="PerMA-Bench Results")

    with doc.head:
        tags.link(rel="stylesheet", href="style.css")

    with doc.body:
        # add fixed sidebar
        with tags.div(cls="sidenav"):
            tags.a("Home", href="index.html", cls="big")
            for bm_name in sorted(benchmark_pngs.keys()):
                tags.a(bm_name, href=bm_name + ".html")

    return doc

def create_benchmark_pages(output_dir, img_dir, benchmark_pngs):
    for bp in benchmark_pngs.items():
        doc = new_html_page(benchmark_pngs)

        with doc.body:
            # add benchmark name as heading
            tags.h1(bp[0])

            # check if first png name of current bm ends with "raw"
            is_raw_json = bp[1][0].endswith("raw.png")

            # add table with configs (for raw jsons)
            if is_raw_json:
                tags.h4("Benchmark Configs")

                with tags.table().add(tags.tbody()):
                    for config in raw_reader.get_raw_configs(bp[0]).items():
                        row = tags.tr()
                        row.add(tags.td(config[0]))
                        row.add(tags.td(config[1]))

            # add pngs and matrix argument permutations (for non-raw results)
            tags.h4("Benchmark Results")
            last_first_arg = ""
            last_second_arg = ""

            for png in bp[1]:
                if not is_raw_json:
                    first_arg = png[:-4].split("-")[1]
                    second_arg = png[:-4].split("-")[2]

                    # add single matrix argument as subheading (one dimension)
                    if second_arg in ["average_duration", "bandwidth", "duration_boxplot"]:
                        if png == bp[1][0]:
                            tags.h5(f"Matrix Argument: {first_arg}")

                    # add each matrix argument permutation as subheading (multiple dimensions)
                    elif first_arg != last_first_arg or second_arg != last_second_arg:
                        tags.h5(f"Current Matrix Arguments: ({first_arg}, {second_arg})")
                        last_first_arg = first_arg
                        last_second_arg = second_arg

                # Use relative img path here to allow copying of the output dir
                tags.div(tags.img(src="img/" + png))

        file_name = bp[0] + ".html"
        with open(os.path.join(output_dir, file_name), "w") as file:
            file.write(doc.render())


def create_index_page(output_dir, benchmark_pngs):
    doc = new_html_page(benchmark_pngs)

    with doc.body:
        tags.h1("PerMA-Bench Results")
        tags.p("Put description text here.")

    with open(os.path.join(output_dir, "index.html"), "w") as file:
        file.write(doc.render())


def init(output_dir, img_dir):
    # collect pngs of each benchmark
    benchmark_pngs = defaultdict(list)
    for path in glob.glob(img_dir + "/*.png"):
        png_name = os.path.basename(path)
        benchmark_name = png_name.split("-")[0]
        benchmark_pngs[benchmark_name].append(png_name)

    # sort pngs of each benchmark for matrix argument extraction in create_benchmark_pages()
    benchmark_pngs = {bm: sorted(pngs) for bm, pngs in benchmark_pngs.items()}

    shutil.copyfile("viz/html/style.css", os.path.join(output_dir, "style.css"))

    create_index_page(output_dir, benchmark_pngs)
    create_benchmark_pages(output_dir, img_dir, benchmark_pngs)
