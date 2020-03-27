# RO help

[![GitHub contributors](https://img.shields.io/github/contributors/code4romania/ro-help.svg?style=for-the-badge)](https://github.com/code4romania/ro-help/graphs/contributors) [![GitHub last commit](https://img.shields.io/github/last-commit/code4romania/ro-help.svg?style=for-the-badge)](https://github.com/code4romania/ro-help/commits/master) [![License: MPL 2.0](https://img.shields.io/badge/license-MPL%202.0-brightgreen.svg?style=for-the-badge)](https://opensource.org/licenses/MPL-2.0)

This project is the result of the 2019 Civic Labs research. You can view the knowledge base of the project, as well as the prototype, on the [ROHelp](https://civiclabs.ro/ro/solutions/aid-management-hub) Civic Labs page.

ROHelp is a platform meant to help NGOs organize their activities during an emergency situation. Initially prototyped with an earthquake in mind, this project was pushed at the forefront of our [Tech for Social Good](https://tfsg.code4.ro/ro/) development program during the COVID-19 pandemic.

[See the project live](https://dev.rohelp.ro/)

Objective: Safe and coherent collection of aid.

How: The application shows verified and validated NGOs for the collection and distribution of resources.

Concept developed as part of the Civic Labs program of Code for Romania.

[Contributing](#contributing) | [Built with](#built-with) | [Deployment](#deployment) | [Feedback](#feedback) | [License](#license) | [About Code4Ro](#about-code4ro)

## Contributing

This project is built by amazing volunteers and you can be one of them! Here's a list of ways in [which you can contribute to this project](.github/CONTRIBUTING.md).
If you want to make any change to this repository, please **make a fork first**.

## Built With

Django

### Programming languages

Python 3

### Development
Docker is used to run the development version, so you'll need to install [Docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/).
Once installed, you just need to copy `cp .env.example .env` and run `docker-compose up` and point your browser to http://localhost:8000/,

A seed command is being run on each start, so you can have fresh new random data to play with. 

If you want to make migrations, run tests or add a dependency, you can get into the web container using:
```bash
docker-compose exec web sh
./manage makemigrations
pip install <my cool dependency>
```

We're using black for formatting and each push is check against it. Running 
```bash
black --line-length 120 --target-version py37
```
before a commit will do the trick.

## Deployment
The deployment process is fully automated using AWS CodeBuild and ECS. Each time a PR is merged on master, a new docker image build is trigger and if 
it's successful, https://dev.rohelp.ro/ will point to your latest changes.

## Feedback

* Request a new feature on GitHub.
* Vote for popular feature requests.
* File a bug in GitHub Issues.
* Email us with other feedback contact@code4.ro

## License

This project is licensed under the MPL 2.0 License - see the [LICENSE](LICENSE) file for details

## About Code4Ro

Started in 2016, Code for Romania is a civic tech NGO, official member of the Code for All network. We have a community of over 500 volunteers (developers, ux/ui, communications, data scientists, graphic designers, devops, it security and more) who work pro-bono for developing digital solutions to solve social problems. #techforsocialgood. If you want to learn more details about our projects [visit our site](https://www.code4.ro/en/) or if you want to talk to one of our staff members, please e-mail us at contact@code4.ro.

Last, but not least, we rely on donations to ensure the infrastructure, logistics and management of our community that is widely spread across 11 timezones, coding for social change to make Romania and the world a better place. If you want to support us, [you can do it here](https://code4.ro/en/donate/).
