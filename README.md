# UW Capstone project: Leveraging AI to Identify the KOL of the Future

This project is a capstone project offered by the department of electrical engineering in University of Washington and cooperated with Genmab, an international biotech company specializing in antibody therapeutics for the treatment of cancer and other serious diseases. This project aims to develop a machine learning powered application to map current KOLs with the highest influence and predict future leaders in medicine field.

You can access the deployed version with this link: https://findkol-5c3f8fcc2a43.herokuapp.com/search/

# Overview

The entire system consist of several things: 
- The python script to pull down the dataset from PubMed.
- The core machine learning (ML) algorithm to provide a list of KOLs for certain disease
- A back-end system with database to store those lists
- A front-end web page UI for user to search the result

Those code is inside the following folder:
- Dataset Build: The python script use in pull down data.
- Model Training and Ranking: The python script use in data preprocessing, constructing graph (citation network), train the Graph Neural Network (GNN) with predefined datasets, inferencing the input dataset, and outputting the ranking result. The GNN part is referenced this repository, https://github.com/sunilkmaurya/GNN_Ranking , and the corresponding paper.
- Back-End and Front-End: The python script for the back-end and front-end, constructing with Django, and the MySQL database to store the results.

# Install and run the code

Dataset Build: 
Just open this folder and run the following cmd.

```bash
python get_data.py
```

The output should be inside data/Immunology or data/Oncology

Model Training and Ranking: 
You would need the following packages: Pytorch, NetworKit, NetworkX and SciPy. Please use PyTorch (0.4.1) and Python (3.7).
After you have installed those packages, just open this folder and run the following cmd.

```bash
python predict.py
```

The output should be inside datasets/res/Immunology or datasets/res/Oncology.

Back-End and Front-End:

You could execute this part of code with docker. Use the following command to build, set up the database, and run the server.

```bash
docker-compose up --build
```

You can access the website in localhost:8000/search. If you want to add the data into database, please access the following url.

```bash
localhost:8000/add
```

# Acknowedgement

I want thank the developers of the GNN repository, which its code plays an important part in this project. The github of GNN would be: https://github.com/sunilkmaurya/GNN_Ranking. You can find the code and the guideline about using it for here. I also want to give my thanks to Manyu and Yizhou, who are two great teammates. Finally I want to thank University of Washington and Genmab to me such an opportunity to learn and solve this real world problem.

This project would not have been possible without your support and contributions!


