import matplotlib.pyplot as plt


def plot_graph(passed_percentage, failed_percentage):
    # Create a pie chart
    plt.figure(figsize=(2, 2))
    labels = ['Passed(%)', 'Failed(%)']
    sizes = [passed_percentage, failed_percentage]   
    explode = (0, 0)  
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax1.axis('equal')  
    plt.tight_layout()
    #plt.show()
    return plt