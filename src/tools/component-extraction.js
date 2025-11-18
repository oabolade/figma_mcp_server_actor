/**
 * Component Extraction Tools
 * MCP tools for extracting and analyzing Figma components
 */

export function registerComponentExtractionTools(protocol, figmaClient) {
    // List components
    protocol.registerTool('list_components', {
        description: 'List all components available in a Figma file',
        inputSchema: {
            type: 'object',
            properties: {
                fileKey: {
                    type: 'string',
                    description: 'Figma file key',
                },
            },
            required: ['fileKey'],
        },
        handler: async (args) => {
            const { fileKey } = args;
            
            const fileData = await figmaClient.getFile(fileKey);

            const components = fileData.components || {};
            const componentSets = fileData.componentSets || {};

            return {
                fileKey,
                components: Object.values(components).map(comp => ({
                    key: comp.key,
                    name: comp.name,
                    description: comp.description || '',
                    componentSetId: comp.componentSetId,
                })),
                componentSets: Object.values(componentSets).map(set => ({
                    key: set.key,
                    name: set.name,
                    description: set.description || '',
                })),
            };
        },
    });

    // Get component details
    protocol.registerTool('get_component_details', {
        description: 'Get detailed information about a specific component including properties and variants',
        inputSchema: {
            type: 'object',
            properties: {
                fileKey: {
                    type: 'string',
                    description: 'Figma file key',
                },
                componentKey: {
                    type: 'string',
                    description: 'Component key (ID)',
                },
            },
            required: ['fileKey', 'componentKey'],
        },
        handler: async (args) => {
            const { fileKey, componentKey } = args;
            
            const fileData = await figmaClient.getFile(fileKey);

            const components = fileData.components || {};
            const component = components[componentKey];

            if (!component) {
                throw new Error(`Component ${componentKey} not found in file`);
            }

            // Find the node in the document tree
            const findNode = (node, targetId) => {
                if (node.id === targetId) {
                    return node;
                }
                if (node.children) {
                    for (const child of node.children) {
                        const found = findNode(child, targetId);
                        if (found) return found;
                    }
                }
                return null;
            };

            const componentNode = findNode(fileData.document, componentKey);

            return {
                fileKey,
                component: {
                    key: component.key,
                    name: component.name,
                    description: component.description || '',
                    componentSetId: component.componentSetId,
                    documentationLinks: component.documentationLinks || [],
                    node: componentNode ? {
                        id: componentNode.id,
                        name: componentNode.name,
                        type: componentNode.type,
                        visible: componentNode.visible,
                        locked: componentNode.locked,
                    } : null,
                },
            };
        },
    });

    // Find component usage
    protocol.registerTool('find_component_usage', {
        description: 'Find all instances where a component is used in a Figma file',
        inputSchema: {
            type: 'object',
            properties: {
                fileKey: {
                    type: 'string',
                    description: 'Figma file key',
                },
                componentKey: {
                    type: 'string',
                    description: 'Component key to search for',
                },
            },
            required: ['fileKey', 'componentKey'],
        },
        handler: async (args) => {
            const { fileKey, componentKey } = args;
            
            const fileData = await figmaClient.getFile(fileKey);

            const findInstances = (node, instances = []) => {
                if (node.type === 'INSTANCE' && node.componentId === componentKey) {
                    instances.push({
                        id: node.id,
                        name: node.name,
                        page: node.parent?.name || 'Unknown',
                    });
                }
                if (node.children) {
                    node.children.forEach(child => findInstances(child, instances));
                }
                return instances;
            };

            const instances = findInstances(fileData.document);

            return {
                fileKey,
                componentKey,
                instances: instances,
                count: instances.length,
            };
        },
    });
}


