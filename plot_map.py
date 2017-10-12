import matplotlib.pyplot as plt
import matplotlib
import sqloperations as sql

def execute():
    """
    Produces a plot of the map data
    """

    matplotlib.rcParams['figure.figsize'] = (10.0, 10.0)
    query = sql.execute('curitiba.db',
        '''
        SELECT lat, lon FROM NODES n JOIN ways_nodes wn ON n.id = wn.node_id
        JOIN ways_tags wt ON wn.id = wt.id
        '''
            )
    coordList = query[0]
    lat, lon = zip(*coordList)
    plt.scatter(lat, lon, 0.05, marker='.')
    plt.show()