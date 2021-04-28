"""Template Generator helper module """

import os
import requests

import readme_generator  # pylint: disable=import-error


def parameter_initialize(data):  # pylint: disable=too-many-statements
    # pylint: disable=line-too-long
    """ Set default parameters, as well as all optional ones in a specific order """
    data['parameters']['numberOfInstances'] = "OPTIONAL"
    data['parameters']['vmScaleSetMinCount'] = "OPTIONAL"
    data['parameters']['vmScaleSetMaxCount'] = "OPTIONAL"
    data['parameters']['appInsights'] = "OPTIONAL"
    data['parameters']['scaleOutCpuThreshold'] = "OPTIONAL"
    data['parameters']['scaleInCpuThreshold'] = "OPTIONAL"
    data['parameters']['scaleOutThroughputThreshold'] = "OPTIONAL"
    data['parameters']['scaleInThroughputThreshold'] = "OPTIONAL"
    data['parameters']['scaleOutTimeWindow'] = "OPTIONAL"
    data['parameters']['scaleInTimeWindow'] = "OPTIONAL"
    data['parameters']['adminUsername'] = "MANDATORY"
    data['parameters']['authenticationType'] = "MANDATORY"
    data['parameters']['adminPasswordOrKey'] = "MANDATORY"
    data['parameters']['uniqueLabel'] = "OPTIONAL"
    data['parameters']['dnsLabel'] = "OPTIONAL"
    data['parameters']['instanceName'] = "OPTIONAL"
    data['parameters']['instanceType'] = "MANDATORY"
    data['parameters']['imageName'] = "MANDATORY"
    data['parameters']['bigIpVersion'] = "MANDATORY"
    data['parameters']['numberOfStaticInstances'] = "OPTIONAL"
    data['parameters']['licenseKey1'] = "OPTIONAL"
    data['parameters']['licenseKey2'] = "OPTIONAL"
    data['parameters']['licensedBandwidth'] = "OPTIONAL"
    data['parameters']['bigIqAddress'] = "OPTIONAL"
    data['parameters']['bigIqUsername'] = "OPTIONAL"
    data['parameters']['bigIqPassword'] = "OPTIONAL"
    data['parameters']['bigIqLicensePoolName'] = "OPTIONAL"
    data['parameters']['bigIqLicenseSkuKeyword1'] = "OPTIONAL"
    data['parameters']['bigIqLicenseUnitOfMeasure'] = "OPTIONAL"
    data['parameters']['numberOfAdditionalNics'] = "OPTIONAL"
    data['parameters']['additionalNicLocation'] = "OPTIONAL"
    data['parameters']['additionalNicIpRangeStart'] = "OPTIONAL"
    data['parameters']['numberOfExternalIps'] = "OPTIONAL"
    data['parameters']['vnetAddressPrefix'] = "OPTIONAL"
    data['parameters']['vnetName'] = "OPTIONAL"
    data['parameters']['vnetResourceGroupName'] = "OPTIONAL"
    data['parameters']['mgmtSubnetName'] = "OPTIONAL"
    data['parameters']['mgmtIpAddressRangeStart'] = "OPTIONAL"
    data['parameters']['mgmtIpAddress'] = "OPTIONAL"
    data['parameters']['externalSubnetName'] = "OPTIONAL"
    data['parameters']['externalIpSelfAddressRangeStart'] = "OPTIONAL"
    data['parameters']['externalIpAddressRangeStart'] = "OPTIONAL"
    data['parameters']['externalIpAddressRangeStart'] = "OPTIONAL"
    data['parameters']['internalSubnetName'] = "OPTIONAL"
    data['parameters']['internalIpAddressRangeStart'] = "OPTIONAL"
    data['parameters']['internalIpAddress'] = "OPTIONAL"
    data['parameters']['enableNetworkFailover'] = "OPTIONAL"
    data['parameters']['provisionInternalLoadBalancer'] = "OPTIONAL"
    data['parameters']['internalLoadBalancerProbePort'] = "OPTIONAL"
    data['parameters']['avSetChoice'] = "OPTIONAL"
    data['parameters']['solutionDeploymentName'] = "OPTIONAL"
    data['parameters']['applicationProtocols'] = "OPTIONAL"
    data['parameters']['applicationAddress'] = "OPTIONAL"
    data['parameters']['applicationServiceFqdn'] = "OPTIONAL"
    data['parameters']['applicationPort'] = "OPTIONAL"
    data['parameters']['applicationSecurePort'] = "OPTIONAL"
    data['parameters']['sslCert'] = "OPTIONAL"
    data['parameters']['sslPswd'] = "OPTIONAL"
    data['parameters']['applicationType'] = "OPTIONAL"
    data['parameters']['blockingLevel'] = "OPTIONAL"
    data['parameters']['customPolicy'] = "OPTIONAL"
    data['parameters']['dnsMemberIpType'] = "OPTIONAL"
    data['parameters']['dnsMemberPort'] = "OPTIONAL"
    data['parameters']['dnsProviderHost'] = "OPTIONAL"
    data['parameters']['dnsProviderPort'] = "OPTIONAL"
    data['parameters']['dnsProviderUser'] = "OPTIONAL"
    data['parameters']['dnsProviderPassword'] = "OPTIONAL"
    data['parameters']['dnsProviderPool'] = "OPTIONAL"
    data['parameters']['dnsProviderDataCenter'] = "OPTIONAL"
    data['parameters']['tenantId'] = "OPTIONAL"
    data['parameters']['clientId'] = "OPTIONAL"
    data['parameters']['servicePrincipalSecret'] = "OPTIONAL"
    data['parameters']['notificationEmail'] = "OPTIONAL"
    data['parameters']['managedRoutes'] = "OPTIONAL"
    data['parameters']['ntpServer'] = "MANDATORY"
    data['parameters']['timeZone'] = "MANDATORY"
    data['parameters']['customImage'] = "OPTIONAL"
    data['parameters']['restrictedSrcAddress'] = "MANDATORY"
    data['parameters']['tagValues'] = "MANDATORY"
    data['parameters']['allowUsageAnalytics'] = "MANDATORY"

    return data


def variable_initialize(data):  # pylint: disable=too-many-statements
    # pylint: disable=line-too-long
    """ Set default variables, as well as all optional ones in a specific order """
    data['variables']['imageNameArray'] = "OPTIONAL"
    data['variables']['imageNameSub'] = "OPTIONAL"
    data['variables']['paygOfferMap'] = "OPTIONAL"
    data['variables']['paygImageMap'] = "OPTIONAL"
    data['variables']['bigIpNicPortMap'] = {
        "1": {
            "Port": "[parameters('bigIpVersion')]"
        },
        "2": {
            "Port": "443"
            },
        "3": {
            "Port": "443"
            },
        "4": {
            "Port": "443"
        },
        "5": {
            "Port": "443"
        },
        "6": {
            "Port": "443"
        }
    }
    data['variables']['bigIpVersionPortMap'] = "MANDATORY"
    data['variables']['computeApiVersion'] = "MANDATORY"
    data['variables']['networkApiVersion'] = "MANDATORY"
    data['variables']['storageApiVersion'] = "MANDATORY"
    data['variables']['appInsightsApiVersion'] = "OPTIONAL"
    data['variables']['appInsightsComponentsApiVersion'] = "OPTIONAL"
    data['variables']['location'] = "[resourceGroup().location]"
    data['variables']['adminPasswordOrKey'] = "MANDATORY"
    data['variables']['linuxConfiguration'] = "MANDATORY"
    data['variables']['defaultAppInsightsLocation'] = "OPTIONAL"
    data['variables']['appInsightsLocation'] = "OPTIONAL"
    data['variables']['subscriptionID'] = "[subscription().subscriptionId]"
    data['variables']['resourceGroupName'] = "[resourceGroup().name]"
    data['variables']['singleQuote'] = "'"
    data['variables']['f5CloudLibsTag'] = "MANDATORY"
    data['variables']['f5CloudLibsAzureTag'] = "MANDATORY"
    data['variables']['f5NetworksTag'] = "MANDATORY"
    data['variables']['f5CloudIappsTag'] = "MANDATORY"
    data['variables']['f5NetworksSolutionScripts'] = "OPTIONAL"
    data['variables']['verifyHash'] = "MANDATORY"
    data['variables']['installCloudLibs'] = "MANDATORY"
    data['variables']['dnsLabel'] = "[toLower(parameters('dnsLabel'))]"
    data['variables']['imageNameToLower'] = "[toLower(parameters('imageName'))]"
    data['variables']['skuToUse'] = "MANDATORY"
    data['variables']['staticSkuToUse'] = "OPTIONAL"
    data['variables']['offerToUse'] = "MANDATORY"
    data['variables']['staticOfferToUse'] = "OPTIONAL"
    data['variables']['imagePlan'] = {
        "name": "[variables('skuToUse')]",
        "product": "[variables('offerToUse')]",
        "publisher": "f5-networks"
    }
    data['variables']['staticImagePlan'] = "OPTIONAL"
    data['variables']['imageReference'] = {
        "offer": "[variables('offerToUse')]",
        "publisher": "f5-networks",
        "sku": "[variables('skuToUse')]",
        "version": "[parameters('bigIpVersion')]"
    }
    data['variables']['staticImageReference'] = "OPTIONAL"
    data['variables']['bigIpNicPortValue'] = "MANDATORY"
    data['variables']['bigIpMgmtPort'] = "[variables('bigIpVersionPortMap')[variables('bigIpNicPortValue')].Port]"
    data['variables']['instanceName'] = "OPTIONAL"
    data['variables']['newAvailabilitySetName'] = "OPTIONAL"
    data['variables']['availabilitySetName'] = "[concat(variables('dnsLabel'), '-avset')]"
    data['variables']['virtualNetworkName'] = "[concat(variables('dnsLabel'), '-vnet')]"
    data['variables']['vnetId'] = "[resourceId('Microsoft.Network/virtualNetworks', variables('virtualNetworkName'))]"
    data['variables']['vnetAddressPrefix'] = "OPTIONAL"
    data['variables']['publicIPAddressType'] = "Static"
    data['variables']['mgmtPublicIPAddressName'] = "[concat(variables('dnsLabel'), '-mgmt-pip')]"
    data['variables']['mgmtPublicIPAddressId'] = "[resourceId('Microsoft.Network/publicIPAddresses', variables('mgmtPublicIPAddressName'))]"
    data['variables']['mgmtNsgID'] = "[resourceId('Microsoft.Network/networkSecurityGroups/',concat(variables('dnsLabel'),'-mgmt-nsg'))]"
    data['variables']['mgmtNicName'] = "[concat(variables('dnsLabel'), '-mgmt')]"
    data['variables']['mgmtNicID'] = "[resourceId('Microsoft.Network/NetworkInterfaces', variables('mgmtNicName'))]"
    data['variables']['mgmtSubnetName'] = "mgmt"
    data['variables']['mgmtSubnetId'] = "[concat(variables('vnetId'), '/subnets/', variables('mgmtSubnetName'))]"
    data['variables']['mgmtSubnetPrefix'] = "OPTIONAL"
    data['variables']['mgmtSubnetPrivateAddressPrefixArray'] = "OPTIONAL"
    data['variables']['mgmtSubnetPrivateAddressPrefix'] = "OPTIONAL"
    data['variables']['mgmtSubnetPrivateAddressSuffixInt'] = "OPTIONAL"
    data['variables']['mgmtSubnetPrivateAddressSuffix'] = "OPTIONAL"
    data['variables']['mgmtSubnetPrivateAddressSuffix1'] = "OPTIONAL"
    data['variables']['mgmtSubnetPrivateAddress'] = "OPTIONAL"
    data['variables']['mgmtSubnetPrivateAddress1'] = "OPTIONAL"
    data['variables']['extSelfPublicIpAddressNamePrefix'] = "OPTIONAL"
    data['variables']['extSelfPublicIpAddressIdPrefix'] = "OPTIONAL"
    data['variables']['extpublicIPAddressNamePrefix'] = "OPTIONAL"
    data['variables']['extPublicIPAddressIdPrefix'] = "OPTIONAL"
    data['variables']['extNsgID'] = "OPTIONAL"
    data['variables']['extNicName'] = "OPTIONAL"
    data['variables']['extSubnetName'] = "OPTIONAL"
    data['variables']['extSubnetPrefix'] = "OPTIONAL"
    data['variables']['extSubnetId'] = "OPTIONAL"
    data['variables']['extSubnetSelfPrivateAddressPrefixArray'] = "OPTIONAL"
    data['variables']['extSubnetSelfPrivateAddressPrefix'] = "OPTIONAL"
    data['variables']['extSubnetSelfPrivateAddressSuffixInt'] = "OPTIONAL"
    data['variables']['extSubnetSelfPrivateAddressSuffix'] = "OPTIONAL"
    data['variables']['extSubnetPrivateAddress'] = "OPTIONAL"
    data['variables']['extSubnetPrivateAddress1'] = "OPTIONAL"
    data['variables']['extSubnetPrivateAddressPrefixArray'] = "OPTIONAL"
    data['variables']['extSubnetPrivateAddressPrefix'] = "OPTIONAL"
    data['variables']['extSubnetPrivateAddressSuffixInt'] = "OPTIONAL"
    data['variables']['extSubnetPrivateAddressSuffix0'] = "OPTIONAL"
    data['variables']['extSubnetPrivateAddressSuffix1'] = "OPTIONAL"
    data['variables']['intNicName'] = "OPTIONAL"
    data['variables']['intSubnetName'] = "OPTIONAL"
    data['variables']['intSubnetPrefix'] = "OPTIONAL"
    data['variables']['intSubnetId'] = "OPTIONAL"
    data['variables']['intSubnetPrivateAddress'] = "OPTIONAL"
    data['variables']['intSubnetPrivateAddress1'] = "OPTIONAL"
    data['variables']['intSubnetPrivateAddress2'] = "OPTIONAL"
    data['variables']['intSubnetPrivateAddress3'] = "OPTIONAL"
    data['variables']['intSubnetPrivateAddressPrefixArray'] = "OPTIONAL"
    data['variables']['intSubnetPrivateAddressPrefix'] = "OPTIONAL"
    data['variables']['intSubnetPrivateAddressSuffixInt'] = "OPTIONAL"
    data['variables']['intSubnetPrivateAddressSuffix'] = "OPTIONAL"
    data['variables']['intSubnetPrivateAddressSuffix1'] = "OPTIONAL"
    data['variables']['intSubnetPrivateAddressSuffix2'] = "OPTIONAL"
    data['variables']['intSubnetPrivateAddressSuffix3'] = "OPTIONAL"
    data['variables']['internalLoadBalancerAddress'] = "OPTIONAL"
    data['variables']['mgmtSubnetRef'] = "OPTIONAL"
    data['variables']['extSubnetRef'] = "OPTIONAL"
    data['variables']['intSubnetRef'] = "OPTIONAL"
    data['variables']['addtlNicName'] = "OPTIONAL"
    data['variables']['addtlNicFillerArray'] = "OPTIONAL"
    data['variables']['addtlNicRefSplit'] = "OPTIONAL"
    data['variables']['netCmd00'] = "OPTIONAL"
    data['variables']['netCmd01'] = "OPTIONAL"
    data['variables']['netCmd02'] = "OPTIONAL"
    data['variables']['netCmd03'] = "OPTIONAL"
    data['variables']['netCmd04'] = "OPTIONAL"
    data['variables']['netCmd05'] = "OPTIONAL"
    data['variables']['netCmd'] = "OPTIONAL"
    data['variables']['numberOfExternalIps'] = "OPTIONAL"
    data['variables']['mgmtRouteGw'] = "OPTIONAL"
    data['variables']['tmmRouteGw'] = "OPTIONAL"
    data['variables']['routeCmdArray'] = "OPTIONAL"
    data['variables']['subnetArray'] = "OPTIONAL"
    data['variables']['addtlSubnetArray'] = "OPTIONAL"
    data['variables']['selfNicConfigArray'] = "OPTIONAL"
    data['variables']['addtlNicConfigArray'] = "OPTIONAL"
    data['variables']['backEndAddressPoolArray'] = "OPTIONAL"
    data['variables']['failoverCmdArray'] = "OPTIONAL"
    data['variables']['ipAddress'] = "OPTIONAL"
    data['variables']['deviceNamePrefix'] = "OPTIONAL"
    data['variables']['externalLoadBalancerName'] = "OPTIONAL"
    data['variables']['externalLoadBalancerAddress'] = "OPTIONAL"
    data['variables']['extLbId'] = "OPTIONAL"
    data['variables']['internalLoadBalancerName'] = "OPTIONAL"
    data['variables']['intLbId'] = "OPTIONAL"
    data['variables']['frontEndIPConfigID'] = "OPTIONAL"
    data['variables']['vmssName'] = "OPTIONAL"
    data['variables']['vmssId'] = "OPTIONAL"
    data['variables']['staticVmssName'] = "OPTIONAL"
    data['variables']['staticVmssId'] = "OPTIONAL"
    data['variables']['appInsightsName'] = "OPTIONAL"
    data['variables']['appInsightsNameArray'] = "OPTIONAL"
    data['variables']['scaleOutTimeWindow'] = "OPTIONAL"
    data['variables']['scaleInTimeWindow'] = "OPTIONAL"
    data['variables']['cpuMetricName'] = "OPTIONAL"
    data['variables']['throughputMetricName'] = "OPTIONAL"
    data['variables']['scaleMetricMap'] = "OPTIONAL"
    data['variables']['customEmailBaseArray'] = "OPTIONAL"
    data['variables']['customEmail'] = "OPTIONAL"
    data['variables']['lbTcpProbeNameHttp'] = "OPTIONAL"
    data['variables']['lbTcpProbeIdHttp'] = "OPTIONAL"
    data['variables']['lbTcpProbeNameHttps'] = "OPTIONAL"
    data['variables']['lbTcpProbeIdHttps'] = "OPTIONAL"
    data['variables']['httpBackendPort'] = "OPTIONAL"
    data['variables']['httpsBackendPort'] = "OPTIONAL"
    data['variables']['commandArgs'] = "OPTIONAL"
    data['variables']['tagValues'] = "[parameters('tagValues')]"
    data['variables']['staticVmssTagValues'] = "OPTIONAL"
    data['variables']['newDataStorageAccountName'] = "[concat(uniqueString(variables('dnsLabel'), resourceGroup().id, deployment().name), 'data000')]"
    data['variables']['dataStorageAccountType'] = "Standard_LRS"
    data['variables']['deploymentId'] = "MANDATORY"
    data['variables']['allowUsageAnalytics'] = "MANDATORY"
    data['variables']['webVmName'] = "OPTIONAL"
    data['variables']['webVmSubnetPrivateAddress'] = "OPTIONAL"
    data['variables']['webVmVsAddr'] = "OPTIONAL"
    data['variables']['webVmVsPort'] = "OPTIONAL"
    data['variables']['publicIpAddressConfiguration'] = "OPTIONAL"
    data['variables']['customImage'] = "OPTIONAL"
    data['variables']['useCustomImage'] = "OPTIONAL"
    data['variables']['customImageReference'] = "OPTIONAL"
    data['variables']['createNewCustomImage'] = "OPTIONAL"
    data['variables']['newCustomImageName'] = "OPTIONAL"
    data['variables']['storageProfileArray'] = "OPTIONAL"
    data['variables']['staticStorageProfileArray'] = "OPTIONAL"
    data['variables']['premiumInstanceArray'] = "OPTIONAL"
    data['variables']['customConfig'] = "### START (INPUT) CUSTOM CONFIGURATION HERE\n"
    data['variables']['installCustomConfig'] = "[concat(variables('singleQuote'), '#!/bin/bash\n', variables('customConfig'), variables('singleQuote'))]"

    return data


def template_check(data, resource):
    """ Remove extra optional resources (variables, parameters), enforce mandatory parameters """
    for var in data[resource]:
        if data[resource][var] == "OPTIONAL":
            data[resource].pop(var)
        elif data[resource][var] == "MANDATORY":
            raise Exception(f'Mandatory parameter/variable: {var} was not filled in, exiting...')
    return data


def param_descr_update(data, i_data):
    """ Fill in parameter descriptions from the YAML doc file """
    yaml_doc_loc = {'doc_text_file': 'azure/files/readme_files/template_text.yaml'}
    readme_gen = readme_generator.ReadmeGen({}, i_data, {})
    readme_gen.open_files(yaml_doc_loc)
    for param in data:
        if data[param]['metadata']['description'] != "":
            # If parameter description is filled in then don't replace
            continue
        else:
            data[param]['metadata']['description'] = readme_gen.get_custom_text(
                'parameter_list', param)
    return data


def pub_ip_strip(data, resource, tmpl_type):  # pylint: disable=too-many-branches
    """ Set Public IP address value to null within the IP Configuration Objects if exists """
    if resource != 'PublicIpAddress':
        raise Exception('Unknown resource type specified in function.')

    for item in data:  # pylint: disable=too-many-nested-blocks
        if tmpl_type == 'resources' and 'properties' in item:
            obj = 'ipConfigurations'
            if obj in item['properties']:
                # declared as a list
                for ipconfig in range(0, len(item['properties'][obj])):
                    if resource in item['properties'][obj][ipconfig]['properties']:
                        item['properties'][obj][ipconfig]['properties'][resource] = None
            # Check if ipConfigurations is a copy and strip there as well if so
            obj = 'copy'
            if obj in item['properties']:
                for copy in range(0, len(item['properties'][obj])):
                    if resource in item['properties'][obj][copy]['input']['properties']:
                        item['properties'][obj][copy]['input']['properties'][resource] = None
        elif tmpl_type == 'variables':
            try:
                if isinstance(data[item], list):
                    for ipconfig in range(0, len(data[item])):
                        if resource in data[item][ipconfig]['properties']:
                            data[item][ipconfig]['properties'][resource] = None
            except KeyError:
                continue
        else:
            raise Exception('Unknown template type specified in the function.')
    return data


def verify_hash(url, via_url):
    """ Download latest verifyHash to be used by the templates, or pull from local file """
    # verify_hash_file = "azure/files/misc_files/verifyHash"
    verify_hash_file = os.path.join(os.path.dirname(__file__), 'common/verifyHash')
    if via_url:
        response = None
        if url.startswith('https'):
            response = requests.get(url, verify=False)
        else:
            response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Unable to download verify hash file, HTTP Error Response: %s" % (
                response.msg))
        # HTTP Call MIGHT include trailing \n, remove that
        verify_hash_text = response.text
        if verify_hash_text[-1:] == '\n':
            verify_hash_text = verify_hash_text[:-1]
        # Update verifyHash file if not in sync
        with open(verify_hash_file, "r+") as _file:
            if verify_hash_text != _file.read():
                _file.seek(0)
                _file.write(verify_hash_text)
                _file.truncate()
    else:
        with open(verify_hash_file, "r") as _file:
            verify_hash_text = _file.read()
    return verify_hash_text
