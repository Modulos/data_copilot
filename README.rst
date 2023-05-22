

.. image:: frontend/src/assets/icons/svg/logo-landing.svg
   :target: #
   :align: center
   :width: 100%

--------


.. image:: https://pyup.io/repos/github/Modulos/data_copilot/shield.svg
     :target: https://pyup.io/repos/github/Modulos/data_copilot/
     :alt: Updates

.. image:: https://img.shields.io/badge/python-3.10-blue
     :target: #
     :alt: Python Version 3.10

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/psf/black

.. image:: https://github.com/Modulos/data_copilot/actions/workflows/pr-test.yml/badge.svg?event=push
     :target: https://github.com/Modulos/data_copilot/actions/workflows/pr-test.yml

--------

DataCopilot is a scalable, docker-based software solution designed to streamline data processing and analysis. It offers a comprehensive platform that integrates frontend, backend, execution, and scheduling functionalities. Users can conveniently upload files in various formats such as CSV and XLSX, and interactively ask questions about these files, effectively turning complex data into understandable insights. Notably, DataCopilot also serves as a robust framework for building your own prompt-based applications, enhancing user experience and interaction. Future updates are anticipated to expand its file support, further increasing its versatility and utility in data management.




Installation
============

Requirements
------------

Before you can install DataCopilot, you need to make sure you have the following tools installed:

- `Docker <https://docs.docker.com/get-docker/>`_
- `Docker Compose <https://docs.docker.com/compose/install/>`_
- `Python3 <https://www.python.org/downloads/>`_

Each of these tools has its own installation guide. Follow the links to get instructions for your specific operating system (Windows, Mac, or Linux).

Furthermore, you need to have an openai API key. You can get one by signing up for an account at `openai.com <https://beta.openai.com/signup>`_.

Cloning and Setting Up
----------------------


Once you have Docker, Docker Compose, and Python3 installed, you can download and set up DataCopilot. Run the following commands in your terminal:

.. code-block:: bash

    git clone https://github.com/modulos/data_copilot.git
    cd data_copilot
    make setup

These commands will clone the DataCopilot repository and run the setup process.

During the setup process, you will be prompted to enter your openai API key. You can also enter it manually by editing the ``.dev.env`` file in the root directory of the repository after the installation.

Choose `sql` as the compute backend. This will allow you to use the full functionality of DataCopilot. The getting_started compute backend is a limited version which will help you to get started with implementing your own logic. 
Checkout the `Build your own Copilot` section for more information.


Open DataCopilot in your browser: http://localhost


.. image:: assets/login_page.png
   :align: center
   :width: 100%


Maintaining and Updating
------------------------

Running DataCopilot

.. code-block:: bash

    make run

Reset DataCopilot

.. code-block:: bash

    make reset-db




Architecture
============

.. image:: assets/architecture.svg
   :align: center
   :width: 100%

The DataCopilot system is composed of several services, each running in its own Docker container. These services interact to provide a comprehensive data processing and management solution.

- **Nginx:** This service acts as a reverse proxy for the backend and adminer services. It uses the `data-copilot-nginx` Docker image and listens on port 80.

- **Database:** This service runs a PostgreSQL database server, using the `postgres:latest` Docker image. The database data is stored in a Docker volume for persistence.

- **Frontend:** The user interface of the application is provided by the frontend service, using the `data-copilot-frontend` Docker image. The frontend framework is Vue3.

- **Backend:** The main application logic is handled by the backend service. It uses the `data-copilot-backend` Docker image and interacts with the database. The backend framework is `FastAPI <https://github.com/tiangolo/fastapi>`_.

- **Adminer:** This service provides a web interface for managing the PostgreSQL database. It uses the `adminer` Docker image.

- **Redis Queue:** This service manages a job queue for asynchronous tasks. It uses the `redis:alpine` Docker image.

- **Celery Worker:** This service executes the asynchronous tasks from the Redis queue. It uses the `data-copilot-celery-worker` Docker image.

- **Flower:** This service provides a web interface for monitoring the Celery worker tasks. It uses the `data-copilot-celery-flower` Docker image.

The services are interconnected, with data flowing between them as necessary. This architecture allows for scalability, as each component can be scaled independently as per the workload.


Development
===========

Storage
-------

By default, DataCopilot uses local storage for data persistence. The data folder is named `shared-fs` and is created in your current working directory. This setup should be sufficient for most development tasks.

However, for more extensive data handling, DataCopilot supports Azure as a storage backend. This allows you to utilize Azure's scalable and secure storage solutions for your data.

If you choose to use Azure as your storage backend, you will need to set the following environment variables in the `.dev.env` file:

- `AZURE_STORAGE_ACCOUNT_KEY`: Your Azure storage account key.
- `AZURE_STORAGE_ACCOUNT_NAME`: Your Azure storage account name.
- `STORAGE_BACKEND`: The URL of your Azure storage container. The URL should be in the following format: `https://{storage_account}.dfs.core.windows.net/{container}/`.

These environment variables configure the connection to your Azure storage account and specify the storage container to use.

Remember to replace `{storage_account}` with your Azure storage account name and `{container}` with the name of your Azure storage container.


Database
--------

DataCopilot uses PostgreSQL as its database. This provides a robust and scalable solution for data management. 

The default environment variables for connecting to the PostgreSQL database are:

- `POSTGRES_DB`: The name of your PostgreSQL database. The default value is `postgres`.
- `POSTGRES_HOST`: The hostname of your PostgreSQL server. The default value is `database`.
- `POSTGRES_PASSWORD`: The password for your PostgreSQL user. The default value is `postgres`.
- `POSTGRES_PORT`: The port on which your PostgreSQL server is running. The default value is `5432`.
- `POSTGRES_USER`: The username for accessing your PostgreSQL database. The default value is `postgres`.

These default values should work out-of-the-box for most development setups. However, you can change them as needed to match your specific database configuration.


Development and Hot Reloading
-----------------------------

DataCopilot supports hot reloading, which allows you to see the effects of your code changes in real time without needing to manually stop and restart the application. This feature significantly speeds up the development process and provides instant feedback, making it easier to build and iterate on your application.

To start the service with hot reloading enabled, run the following command:

.. code-block:: bash

    make run-dev

This command will start the DataCopilot service in development mode. Now, whenever you make changes to your code, those changes will be immediately reflected in the running application.


Build your own Copilot
----------------------


DataCopilot is not just a standalone application, but also a framework that you can use to build your own data processing and analysis tools. Here are the steps to get started:

1. **Worker Logic:** The worker logic can be found in the `celery_app/apps` directory. You can modify the logic here to suit your specific needs.

2. **Getting Started Example:** For a basic understanding of the worker logic, you can refer to the `celery_app/apps/getting_started_example.py` file. This file provides a simple example that can serve as a starting point for your custom logic.

3. **Executor Logic:** The executor logic is contained in the `celery_app/executors/getting_started_executor.py` file. You can modify this file to customize how tasks are executed.

4. **Supported File Types:** If you want to change the supported file types (e.g., extend support to PDF), you will need to configure this on the backend side in the `backend/config/config.py` file. Additionally, you need to implement the logic for handling the new file type in the `backend/routers/artifacts.py` file.

5. **File Type Interaction:** Once you've configured the backend to support the new file type, you'll need to implement the specific logic for interacting with that file type on the worker side.

6. **Return Types:** Currently, DataCopilot is configured to only return tables to the user. However, the framework supports other return types such as heatmaps, histograms, and barplots. You can see the implementation details for these types in the `getting_started_executor.py` file.

With these steps, you can customize DataCopilot to handle your specific data processing and analysis tasks. Remember to thoroughly test your changes to ensure they work as expected.


Data Copilot Trademark
======================
Data Copilot is a trademark of Modulos AG. 


Current Maintainers
===================
- `Tim Rohner <https://github.com/leokster>`_
- `Dennis Turp <https://github.com/mdturp>`_

Contributors
============

.. list-table::
   :header-rows: 1

   * - Project Leads
     - Backend
     - DevOps
     - Frontend
     - Design
   * - `Dennis Turp <https://github.com/mdturp>`_
     - `Tim Rohner <https://github.com/leokster>`_
     - `Jiri Kralik <https://github.com/jirikralik>`_
     - `Dennis Turp <https://github.com/mdturp>`_
     - `Celina Jong <https://github.com/celinajong>`_
   * - `Tim Rohner <https://github.com/leokster>`_
     - `Dennis Turp <https://github.com/mdturp>`_
     - `Serhii  Kyslyi <https://github.com/serhiikyslyi>`_
     - `Oleh Lukashchuk <https://github.com/Olehlukashchuk96>`_
     - 
   * - 
     - `Michael Röthlisberger <https://github/roethlisbergermichael>`_
     - `Keven Le Moing <https://github.com/KevenLeMoing>`_
     - 
     - 
   * -
     - `Keven Le Moing <https://github.com/KevenLeMoing>`_
     -  
     -  
     -  
   * - 
     - `Andrei Vaduva <https://github.com/andreiv-dev>`_
     - 
     - 
     - 
   * - 
     - `Dominic Stark <https://github.com/dominicstark>`_
     - 
     - 
     - 
   * - 
     - `Tomasz Kucharski <https://github.com/tomkuch>`_
     - 
     - 
     - 


