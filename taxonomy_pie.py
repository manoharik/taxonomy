import matplotlib.pyplot as plt
import numpy as np


y = np.array([12,7,10,30,3,2,32,3,2])
colors = plt.cm.gray(np.linspace(0.2,0.8,5))
t=np.array(["Acquaint_population","Sample_acquaintance","Background_knowledge","Linking_other_dataset","linking_temporal_releases","Populaion_uniqueness","Sample_uniqueness","Sample_synthetic","Uniqueness_elements"])
#plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
plt.pie(y, labels=t,autopct='%1.1f%%',colors=colors)

plt.savefig("taxonomy_pie.pdf", bbox_inches='tight')
plt.show()