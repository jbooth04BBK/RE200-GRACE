
from common_routines import *

def main():

    log_debug("Started!")

    gml_project_path = "Z:\\Projects\\Research\\0200-GRACE\\DataExtraction\\GMLs"
    # file_name = f"initial_demo_{stage}_graph.gml"
    # file_name = "sp01_demo_70_graph.gml"
    # file_name = "sp01_demo_70_graph.graphml"
    file_name = "sp01_demo_73_graph.graphml"
    # file_name = "sp01_demo_12_graph.graphml"
    outFilePath = os.path.join(gml_project_path, file_name)

    log_debug(f"Read file: {file_name}")

    G = nx.read_graphml(outFilePath)

    # layouts = [
    #     # "bipartite",
    #     "circular",
    #     "kamada_kawai",
    #     "random",
    #     # "rescale",
    #     # "rescale_dict",
    #     "shell",
    #     "spring",
    #     "spectral",
    #     # "planar",
    #     "fruchterman_reingold",
    #     "spiral",
    #     # "multipartite",
    # ]

    layouts = [
        "spring",
    ]

    for layout in layouts:
        title = f'<br>Network graph from graphML file: {file_name}, layout: {layout}<br>'
        fig = plot_graph(G, layout=layout, title=title)
        fig.show()

    log_debug("Done!")


if __name__ == "__main__":
    main()
