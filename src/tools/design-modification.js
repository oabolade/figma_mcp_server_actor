/**
 * Design Modification Tools
 * MCP tools for modifying design elements (Note: Limited via REST API, may require Plugin API)
 */

export function registerDesignModificationTools(protocol, figmaClient) {
    // Update node properties (placeholder - REST API has limited write capabilities)
    protocol.registerTool('update_node_properties', {
        description: 'Update properties of a design node (Note: Figma REST API has limited write capabilities. Full modification may require Plugin API)',
        inputSchema: {
            type: 'object',
            properties: {
                fileKey: {
                    type: 'string',
                    description: 'Figma file key',
                },
                nodeId: {
                    type: 'string',
                    description: 'Node ID to update',
                },
                properties: {
                    type: 'object',
                    description: 'Properties to update (structure depends on node type)',
                },
            },
            required: ['fileKey', 'nodeId'],
        },
        handler: async (args) => {
            const { fileKey, nodeId, properties } = args;
            
            // Note: Figma REST API has very limited write capabilities
            // Most modifications require the Plugin API or manual editing
            // This tool provides information about the node and limitations
            
            try {
                const nodeData = await figmaClient.getFileNodes(fileKey, [nodeId]);
                const node = nodeData.nodes[nodeId];

                return {
                    fileKey,
                    nodeId,
                    currentNode: node ? {
                        id: node.document.id,
                        name: node.document.name,
                        type: node.document.type,
                    } : null,
                    message: 'Figma REST API has limited write capabilities. For full design modification, please use:',
                    options: [
                        'Figma Plugin API for programmatic modifications',
                        'Figma web interface for manual edits',
                        'Figma REST API webhooks for event-driven updates',
                    ],
                    requestedProperties: properties,
                    note: 'Consider using the Plugin API or webhooks for comprehensive design modifications',
                };
            } catch (error) {
                throw new Error(`Failed to retrieve node information: ${error.message}`);
            }
        },
    });

    // Get node information for modification planning
    protocol.registerTool('get_node_for_modification', {
        description: 'Get detailed node information to plan modifications (useful before using Plugin API)',
        inputSchema: {
            type: 'object',
            properties: {
                fileKey: {
                    type: 'string',
                    description: 'Figma file key',
                },
                nodeId: {
                    type: 'string',
                    description: 'Node ID',
                },
                includeGeometry: {
                    type: 'boolean',
                    description: 'Include geometry information',
                    default: true,
                },
            },
            required: ['fileKey', 'nodeId'],
        },
        handler: async (args) => {
            const { fileKey, nodeId, includeGeometry = true } = args;
            
            const nodeData = await figmaClient.getFileNodes(fileKey, [nodeId], {
                geometry: includeGeometry,
            });

            const node = nodeData.nodes[nodeId]?.document;

            if (!node) {
                throw new Error(`Node ${nodeId} not found`);
            }

            return {
                fileKey,
                nodeId,
                node: {
                    id: node.id,
                    name: node.name,
                    type: node.type,
                    visible: node.visible,
                    locked: node.locked,
                    ...(includeGeometry && {
                        absoluteBoundingBox: node.absoluteBoundingBox,
                        relativeTransform: node.relativeTransform,
                    }),
                    fills: node.fills,
                    strokes: node.strokes,
                    effects: node.effects,
                    characters: node.characters,
                    style: node.style,
                },
                modificationGuidance: {
                    restApiLimitations: 'REST API has limited write capabilities',
                    recommendedApproach: 'Use Figma Plugin API for programmatic modifications',
                    alternative: 'Use webhooks for event-driven updates',
                },
            };
        },
    });
}


