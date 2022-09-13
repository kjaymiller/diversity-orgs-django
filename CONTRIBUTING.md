# Contributing to the Project

## Read the Code of Conduct
Your contribution to this repo assumes you have read and accept the Development [Code of Conduct](./CODE_OF_CONDUCT).

## About the Project Stack
- The project publicly uses Microsoft Azure to host a Django site. 
- The data is stored via Azure storage
- Azure Maps is utilizing our [API](https://diversityorgs-django.azurewebsites.net).

Although this project is deployed on Azure, the goal is that it can be hosted anywhere with relative ease and little-to-no changes.

## Style
### Black & iSort
This project uses Black and isort to format code. Please run these before submitting a PR.

### Models
The `Organization` model is the main model for this project. Associated models are `Location`, `DiversityFocus`, and `TechnologyFocus`. The models are stoed in [org_pages/models.py](./org_pages/models.py).

### Views
The project uses Django's class-based views. The views are stored in [org_pages/views.py](./org_pages/views.py).

## Developing Django Views
Please use class-based views for all new views created.

## Acknowledgement
Microsoft is the employer of the primary maintainer.




