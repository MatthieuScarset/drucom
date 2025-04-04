# Drucom

Data Analysis of the Drupal Community (Users & Contributions).

## Getting started 

Fetch data from the web:

```bash
# Install requirements:
pip install -r requirements.txt

# Run the installation notebook and follow the steps.
cd notebook/ && jupyter notebook installation.ipynb
```

## Datasets

* Drupal releases:
  * URL: https://www.drupal.org/api-d7/node.json?type=project_core
  * Parameters: 
    * `field_project_type`: `full` to exclude sandbox releases
* ...
* @todo list all API URLs and parameters

## Future developments

* Parse [Community spotlight](https://www.drupal.org/forum/general/community-spotlight) articles to identify key members
* Parse the list of [Drupal local associations](https://www.drupal.org/node/3069614)
* Analyze the sponsors of Drupal Events vs Organizations dataset

## Resources

* [Drupal.org](https://drupal.org/), the community website - managed by the Drupal Association.
* [Drupal GitLab](https://git.drupalcode.org/) instance, hosting core and all other contributed projects' code.
* [Drupal REST APIs](https://www.drupal.org/drupalorg/docs/apis/rest-and-other-apis) - used to source raw data.
* [GitLab REST API](https://docs.gitlab.com/api/rest/) - used to source raw data.