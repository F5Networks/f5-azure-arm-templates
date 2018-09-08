# F5 Azure ARM templates

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)
[![Releases](https://img.shields.io/github/release/f5networks/f5-azure-arm-templates.svg)](https://github.com/f5networks/f5-azure-arm-templates/releases)
[![Issues](https://img.shields.io/github/issues/f5networks/f5-azure-arm-templates.svg)](https://github.com/f5networks/f5-azure-arm-templates/issues)

## Introduction

Welcome to the GitHub repository for F5's ARM templates for Azure deployments.  All of the templates in this repository have been developed by F5 Networks engineers. Across all branches in this repository, there are two directories: *f5_supported* and *experimental*

  - **supported**<br>
  The supported directory contains Azure ARM templates that have been created and fully tested by F5 Networks. These templates are fully supported by F5, meaning you can get assistance if necessary from F5 Technical Support via your typical methods.

  - **experimental**<br>
  The experimental directory also contains ARM templates that have been created by F5 Networks. However, these templates have not completed full testing and are subject to change. F5 Networks does not offer technical support for templates in the experimental directory, so use these templates with caution.

## Template information

Descriptions for each template are contained at the top of each template in the *Description* key.
For additional information, including how the templates are generated, and assistance in deploying a template, see the individual README.md file in the individual template directory.

### Matrix for tagged releases

F5 has created a matrix that contains all of the tagged releases of the F5 ARM templates for Microsoft Azure and the corresponding BIG-IP versions, license types and throughputs available for a specific tagged release. See https://github.com/F5Networks/f5-azure-arm-templates/blob/v5.3.2.0/azure-bigip-version-matrix.md

## CVE-2017-6168 information

If you have launched an F5 ARM template from a prior release, see the <a href="#important">important note</a> at the bottom of this page.

## List of F5 ARM templates for Azure deployments

The following is a list of the current **supported** F5 ARM templates. See the **experimental** directory for experimental templates.
Note that many of the solutions now include *Production Stack* templates.  This means that the templates deploy without creating or attaching any public IP addresses to the BIG-IP VEs, see the individual README files for more information.

-  **Deploying the BIG-IP VE in Azure - Single NIC**
    - [New Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/standalone/1nic/new-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F1nic%2Fnew-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F1nic%2Fnew-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
      - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F1nic%2Fnew-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

    - [Existing Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/standalone/1nic/existing-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F1nic%2Fexisting-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F1nic%2Fexisting-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
      - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F1nic%2Fexisting-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

    - [Production Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/standalone/1nic/production-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F1nic%2Fproduction-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F1nic%2Fproduction-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

-  **Deploying the BIG-IP VE in Azure - 2 NICs**
    - [New Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/standalone/2nic/new-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F2nic%2Fnew-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F2nic%2Fnew-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
      - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F2nic%2Fnew-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

    - [Existing Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/standalone/2nic/existing-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F2nic%2Fexisting-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F2nic%2Fexisting-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
      - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F2nic%2Fexisting-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

    - [Production Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/standalone/2nic/production-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F2nic%2Fproduction-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F2nic%2Fproduction-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

- **Deploying the BIG-IP VE in Azure - 3 NICs**
    - [New Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/standalone/3nic/new-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F3nic%2Fnew-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F3nic%2Fnew-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
      - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F3nic%2Fnew-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

    - [Existing Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/standalone/3nic/existing-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F3nic%2Fexisting-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F3nic%2Fexisting-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
      - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F3nic%2Fexisting-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

    - [Production Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/standalone/3nic/production-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F3nic%2Fproduction-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2F3nic%2Fproduction-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

- **Deploying the BIG-IP VE in Azure - N NICs**
    - [New Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/standalone/n-nic/new-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2Fn-nic%2Fnew-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2Fn-nic%2Fnew-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
      - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2Fn-nic%2Fnew-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

    - [Existing Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/standalone/n-nic/existing-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2Fn-nic%2Fexisting-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2Fn-nic%2Fexisting-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
      - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2Fn-nic%2Fexisting-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

    - [Production Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/standalone/n-nic/production-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2Fn-nic%2Fproduction-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fstandalone%2Fn-nic%2Fproduction-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

- **Deploying the BIG-IP VE in Azure - HA Cluster: Active/Active**
    - *Single NIC*
      - [New Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/failover/same-net/via-lb/1nic/new-stack)
        - *BYOL* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-lb%2F1nic%2Fnew-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
        - *PAYG* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-lb%2F1nic%2Fnew-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
        - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-lb%2F1nic%2Fnew-stack%2Fbigiq%2Fazuredeploy.json"> <img src="http://azuredeploy.net/deploybutton.png"/></a>

      - [Existing Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/failover/same-net/via-lb/1nic/existing-stack)
        - *BYOL* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-lb%2F1nic%2Fexisting-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
        - *PAYG* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-lb%2F1nic%2Fexisting-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
        - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-lb%2F1nic%2Fexisting-stack%2Fbigiq%2Fazuredeploy.json"> <img src="http://azuredeploy.net/deploybutton.png"/></a>

    - *3 NICs*
      - [New Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/failover/same-net/via-lb/3nic/new-stack)
        - *BYOL* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-lb%2F3nic%2Fnew-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
        - *PAYG* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-lb%2F3nic%2Fnew-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
        - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-lb%2F3nic%2Fnew-stack%2Fbigiq%2Fazuredeploy.json"> <img src="http://azuredeploy.net/deploybutton.png"/></a>

      - [Existing Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/failover/same-net/via-lb/3nic/existing-stack)
        - *BYOL* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-lb%2F3nic%2Fexisting-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
        - *PAYG* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-lb%2F3nic%2Fexisting-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
        - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-lb%2F3nic%2Fexisting-stack%2Fbigiq%2Fazuredeploy.json"> <img src="http://azuredeploy.net/deploybutton.png"/></a>

- **Deploying the BIG-IP VE in Azure - HA Cluster: Active/Standby**
  - [New Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/failover/same-net/via-api/n-nic/new-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-api%2Fn-nic%2Fnew-stack%2Fbyol%2Fazuredeploy.json">   <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-api%2Fn-nic%2Fnew-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
      - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-api%2Fn-nic%2Fnew-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

  - [Existing Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/failover/same-net/via-api/n-nic/existing-stack)
      - *BYOL* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-api%2Fn-nic%2Fexisting-stack%2Fbyol%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a><br>
      - *PAYG* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-api%2Fn-nic%2Fexisting-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
      - *Using BIG-IQ for Licensing* <br><a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Ffailover%2Fsame-net%2Fvia-api%2Fn-nic%2Fexisting-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

- **Deploying the BIG-IP VE in Azure - AutoScale BIG-IP LTM - VM Scale Set**
    - *Frontend via ALB*
      - [New Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/autoscale/ltm/via-lb/1nic/new-stack)
          - *PAYG* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fltm%2Fvia-lb%2F1nic%2Fnew-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
          - *Using BIG-IQ for Licensing* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fltm%2Fvia-lb%2F1nic%2Fnew-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

      - [Existing Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/autoscale/ltm/via-lb/1nic/existing-stack)
          - *PAYG* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fltm%2Fvia-lb%2F1nic%2Fexisting-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
          - *Using BIG-IQ for Licensing* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fltm%2Fvia-lb%2F1nic%2Fexisting-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

    - *Frontend via DNS*
      - [New Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/autoscale/ltm/via-dns/1nic/new-stack)
          - *PAYG* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fltm%2Fvia-dns%2F1nic%2Fnew-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
          - *Using BIG-IQ for Licensing* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fltm%2Fvia-dns%2F1nic%2Fnew-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

      - [Existing Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/autoscale/ltm/via-dns/1nic/existing-stack)
          - *PAYG* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fltm%2Fvia-dns%2F1nic%2Fexisting-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
          - *Using BIG-IQ for Licensing* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fltm%2Fvia-dns%2F1nic%2Fexisting-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>


- **Deploying the BIG-IP VE in Azure - Auto Scale BIG-IP WAF (LTM + ASM) - VM Scale Set**
    - *Frontend via ALB* 
      - [New Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/autoscale/waf/via-lb/1nic/new-stack)
          - *PAYG* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fwaf%2Fvia-lb%2F1nic%2Fnew-stack%2Fpayg%2Fazuredeploy.json"> <img src="http://azuredeploy.net/deploybutton.png"/></a>
          - *Using BIG-IQ for Licensing* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fwaf%2Fvia-lb%2F1nic%2Fnew-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
      - [Existing Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/autoscale/waf/via-lb/1nic/existing-stack)
          - *PAYG* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fwaf%2Fvia-lb%2F1nic%2Fexisting-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
          - *Using BIG-IQ for Licensing* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fwaf%2Fvia-lb%2F1nic%2Fexisting-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

    - *Frontend via DNS* 
      - [New Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/autoscale/waf/via-dns/1nic/new-stack)
          - *PAYG* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fwaf%2Fvia-dns%2F1nic%2Fnew-stack%2Fpayg%2Fazuredeploy.json"> <img src="http://azuredeploy.net/deploybutton.png"/></a>
          - *Using BIG-IQ for Licensing* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fwaf%2Fvia-dns%2F1nic%2Fnew-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
      - [Existing Networking Stack](https://github.com/F5Networks/f5-azure-arm-templates/tree/v5.3.2.0/supported/autoscale/waf/via-dns/1nic/existing-stack)
          - *PAYG* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fwaf%2Fvia-dns%2F1nic%2Fexisting-stack%2Fpayg%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>
          - *Using BIG-IQ for Licensing* <br> <a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FF5Networks%2Ff5-azure-arm-templates%2Fv5.3.2.0%2Fsupported%2Fautoscale%2Fwaf%2Fvia-dns%2F1nic%2Fexisting-stack%2Fbigiq%2Fazuredeploy.json">  <img src="http://azuredeploy.net/deploybutton.png"/></a>

---

<a name="important"></a>
<table>
 <tr>
  <td align=center>:warning: <strong>Important<strong> :warning:  </td>
 </tr>
 <tr>
  <td>If you used an F5 ARM template prior to <a href="https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v4.2.0.0">release 4.2.0.0</a>, BIG-IP virtual servers configured with a Client SSL profile may be vulnerable to an Adaptive Chosen Ciphertext attack (AKA Bleichenbacher attack, CVE-2017-6168). For complete information on this vulnerability, see https://support.f5.com/csp/article/K21905460. <br>F5 has released hotfixes for all vulnerable releases. <strong><em>All of the templates in the current release in this repository use non-vulnerable BIG-IP VE images</em></strong>.  If you are using a BIG-IP image launched from a previous version of a template, use the following guidance:<br> <br>  
   <ul>
    <li><em>If you have an existing BIG-IP VE deployment in Azure</em>  <br>See the <a href="https://support.f5.com/csp/article/K21905460">Security Advisory</a>, which contains information about upgrading your BIG-IP VE to a non-vulnerable version.</li>
    <li><em>For <strong>new</strong> BIG-IP VE deployments in Azure</em><br> The F5 ARM templates in <a href="https://github.com/F5Networks/f5-azure-arm-templates/releases/tag/v4.2.0.0">release 4.2.0.0</a> and later use non-vulnerable images. We recommending using the templates in the <a href="https://github.com/F5Networks/f5-azure-arm-templates/releases">latest release</a> for new deployments.</li>
    <li><em>For <strong>new</strong> BIG-IP VE deployments using a template in an older tagged release on GitHub</em><br>  If you have a specific need for using an older F5 ARM template, see <a href="azure-update-bigip-image.md">Changing the BIG-IP VE image in an F5 ARM template</a> for instructions on updating the BIG-IP images referenced in the template.</li>
   </ul>
  </td>
 </tr>
 </table>

### Copyright

Copyright 2014-2018 F5 Networks Inc.

### License

#### Apache V2.0

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.

#### Contributor License Agreement

Individuals or business entities who contribute to this project must have
completed and submitted the [F5 Contributor License Agreement](http://f5-openstack-docs.readthedocs.io/en/latest/cla_landing.html).
