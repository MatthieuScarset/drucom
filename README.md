# Drucom

Data Analysis of the Drupal Community (Users & Contributions).

## Getting started 

Fetch data from the web and merge into one JSON file per entity.

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

# Merge data.
chmod +x ./script/merge_drupal_data.sh
./script/merge_drupal_data.sh event
./script/merge_drupal_data.sh organization
./script/merge_drupal_data.sh user
```

Install requirements:

```bash
pip install -r requirements.txt
```

Open the notebooks:

```bash
cd notebook/
jupyter notebook
```

## Resources

* [Drupal.org](https://drupal.org/), the community website - managed by the Drupal Association.
* [Drupal GitLab](https://git.drupalcode.org/) instance, hosting core and all other contributed projects' code.
* [Drupal REST APIs](https://www.drupal.org/drupalorg/docs/apis/rest-and-other-apis) - used to source raw data.
* [GitLab REST API](https://docs.gitlab.com/api/rest/) - used to source raw data.