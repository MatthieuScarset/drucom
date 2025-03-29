# Drucom

Data Analysis of the Drupal Community (Users & Contributions).

## Getting started 

Fetch data from the web:

```bash
# =====================================================
# Delete existing data if you want to fetch fresh data.
# rm -rf ../data/json/pages_*
# =====================================================

# Fetch data.
# /!\ Warning: this is a very long running script!
chmod +x ./script/fetch_drupal_data.sh
./script/fetch_drupal_data.sh event
./script/fetch_drupal_data.sh organization
./script/fetch_drupal_data.sh user
./script/fetch_drupal_data.sh module
./script/fetch_drupal_data.sh module_terms

# Install requirements:
pip install -r requirements.txt

# Run the installation notebook.
cd notebook/ && jupyter notebook installation.ipynb

# It should have created a `user_uids.json` file.

# Fetch additional data.
chmod +x ./script/fetch_comments_data.sh
./script/fetch_comments_data.sh
```

## Resources

* [Drupal.org](https://drupal.org/), the community website - managed by the Drupal Association.
* [Drupal GitLab](https://git.drupalcode.org/) instance, hosting core and all other contributed projects' code.
* [Drupal REST APIs](https://www.drupal.org/drupalorg/docs/apis/rest-and-other-apis) - used to source raw data.
* [GitLab REST API](https://docs.gitlab.com/api/rest/) - used to source raw data.