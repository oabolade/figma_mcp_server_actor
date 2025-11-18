/**
 * Asset Export Tools
 * MCP tools for exporting Figma assets in various formats
 */

export function registerAssetExportTools(protocol, figmaClient) {
    // Export node
    protocol.registerTool('export_node', {
        description: 'Export a specific node (component, frame, etc.) as an image in PNG, SVG, PDF, or JPG format',
        inputSchema: {
            type: 'object',
            properties: {
                fileKey: {
                    type: 'string',
                    description: 'Figma file key',
                },
                nodeId: {
                    type: 'string',
                    description: 'Node ID to export',
                },
                format: {
                    type: 'string',
                    enum: ['PNG', 'SVG', 'PDF', 'JPG'],
                    description: 'Export format',
                    default: 'PNG',
                },
                scale: {
                    type: 'number',
                    description: 'Scale factor (1x, 2x, 3x, etc.)',
                    default: 1,
                },
            },
            required: ['fileKey', 'nodeId'],
        },
        handler: async (args) => {
            const { fileKey, nodeId, format = 'PNG', scale = 1 } = args;
            
            const imageData = await figmaClient.getImages(fileKey, {
                ids: [nodeId],
                format,
                scale,
            });

            const imageUrl = imageData.images[nodeId];

            if (!imageUrl) {
                throw new Error(`Failed to export node ${nodeId}`);
            }

            return {
                fileKey,
                nodeId,
                format,
                scale,
                url: imageUrl,
                error: imageData.err || null,
            };
        },
    });

    // Export multiple nodes
    protocol.registerTool('export_multiple_nodes', {
        description: 'Export multiple nodes from a Figma file in a specified format',
        inputSchema: {
            type: 'object',
            properties: {
                fileKey: {
                    type: 'string',
                    description: 'Figma file key',
                },
                nodeIds: {
                    type: 'array',
                    items: {
                        type: 'string',
                    },
                    description: 'Array of node IDs to export',
                },
                format: {
                    type: 'string',
                    enum: ['PNG', 'SVG', 'PDF', 'JPG'],
                    description: 'Export format',
                    default: 'PNG',
                },
                scale: {
                    type: 'number',
                    description: 'Scale factor',
                    default: 1,
                },
            },
            required: ['fileKey', 'nodeIds'],
        },
        handler: async (args) => {
            const { fileKey, nodeIds, format = 'PNG', scale = 1 } = args;
            
            if (!Array.isArray(nodeIds) || nodeIds.length === 0) {
                throw new Error('nodeIds must be a non-empty array');
            }

            const imageData = await figmaClient.getImages(fileKey, {
                ids: nodeIds,
                format,
                scale,
            });

            const exports = nodeIds.map(nodeId => ({
                nodeId,
                url: imageData.images[nodeId] || null,
                error: imageData.err || null,
            }));

            return {
                fileKey,
                format,
                scale,
                exports,
                successCount: exports.filter(e => e.url).length,
                errorCount: exports.filter(e => !e.url).length,
            };
        },
    });

    // Export file pages
    protocol.registerTool('export_file_pages', {
        description: 'Export all pages from a Figma file as images',
        inputSchema: {
            type: 'object',
            properties: {
                fileKey: {
                    type: 'string',
                    description: 'Figma file key',
                },
                format: {
                    type: 'string',
                    enum: ['PNG', 'SVG', 'PDF', 'JPG'],
                    description: 'Export format',
                    default: 'PNG',
                },
                scale: {
                    type: 'number',
                    description: 'Scale factor',
                    default: 1,
                },
            },
            required: ['fileKey'],
        },
        handler: async (args) => {
            const { fileKey, format = 'PNG', scale = 1 } = args;
            
            // First get file structure to find page IDs
            const fileData = await figmaClient.getFile(fileKey);
            
            const pageIds = fileData.document.children
                .filter(child => child.type === 'CANVAS')
                .map(page => page.id);

            if (pageIds.length === 0) {
                return {
                    fileKey,
                    format,
                    scale,
                    exports: [],
                    message: 'No pages found in file',
                };
            }

            const imageData = await figmaClient.getImages(fileKey, {
                ids: pageIds,
                format,
                scale,
            });

            const exports = pageIds.map((pageId, index) => {
                const page = fileData.document.children[index];
                return {
                    pageId,
                    pageName: page.name,
                    url: imageData.images[pageId] || null,
                    error: imageData.err || null,
                };
            });

            return {
                fileKey,
                format,
                scale,
                exports,
                successCount: exports.filter(e => e.url).length,
                errorCount: exports.filter(e => !e.url).length,
            };
        },
    });
}


