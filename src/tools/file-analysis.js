/**
 * File Analysis Tools
 * MCP tools for analyzing Figma design files
 */

export function registerFileAnalysisTools(protocol, figmaClient) {
    // Analyze file structure
    protocol.registerTool('analyze_file', {
        description: 'Analyze a Figma file structure, extracting metadata, pages, and top-level components',
        inputSchema: {
            type: 'object',
            properties: {
                fileKey: {
                    type: 'string',
                    description: 'Figma file key (from file URL)',
                },
                includeGeometry: {
                    type: 'boolean',
                    description: 'Include geometry information in the analysis',
                    default: false,
                },
            },
            required: ['fileKey'],
        },
        handler: async (args) => {
            const { fileKey, includeGeometry = false } = args;
            
            const fileData = await figmaClient.getFile(fileKey, {
                geometry: includeGeometry,
            });

            return {
                fileKey,
                name: fileData.name,
                lastModified: fileData.lastModified,
                version: fileData.version,
                thumbnailUrl: fileData.thumbnailUrl,
                document: {
                    id: fileData.document.id,
                    type: fileData.document.type,
                    children: fileData.document.children?.map(page => ({
                        id: page.id,
                        name: page.name,
                        type: page.type,
                        childrenCount: page.children?.length || 0,
                    })) || [],
                },
                components: fileData.components || {},
                componentSets: fileData.componentSets || {},
                styles: fileData.styles || {},
                schemaVersion: fileData.schemaVersion,
            };
        },
    });

    // Get file structure
    protocol.registerTool('get_file_structure', {
        description: 'Get the hierarchical structure of a Figma file including pages and layers',
        inputSchema: {
            type: 'object',
            properties: {
                fileKey: {
                    type: 'string',
                    description: 'Figma file key',
                },
                depth: {
                    type: 'integer',
                    description: 'Depth of the tree to retrieve (default: 1)',
                    default: 1,
                },
            },
            required: ['fileKey'],
        },
        handler: async (args) => {
            const { fileKey, depth = 1 } = args;
            
            const fileData = await figmaClient.getFile(fileKey, {
                depth,
            });

            const extractStructure = (node, currentDepth = 0) => {
                if (currentDepth >= depth) {
                    return { id: node.id, name: node.name, type: node.type };
                }

                return {
                    id: node.id,
                    name: node.name,
                    type: node.type,
                    children: node.children?.map(child => extractStructure(child, currentDepth + 1)) || [],
                };
            };

            return {
                fileKey,
                structure: extractStructure(fileData.document),
            };
        },
    });

    // Extract styles
    protocol.registerTool('extract_styles', {
        description: 'Extract design tokens, styles, and design system information from a Figma file',
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

            const styles = fileData.styles || {};
            const components = fileData.components || {};
            const componentSets = fileData.componentSets || {};

            return {
                fileKey,
                styles: {
                    fills: Object.values(styles).filter(s => s.styleType === 'FILL'),
                    strokes: Object.values(styles).filter(s => s.styleType === 'STROKE'),
                    effects: Object.values(styles).filter(s => s.styleType === 'EFFECT'),
                    text: Object.values(styles).filter(s => s.styleType === 'TEXT'),
                },
                components: Object.values(components).map(comp => ({
                    key: comp.key,
                    name: comp.name,
                    description: comp.description,
                })),
                componentSets: Object.values(componentSets).map(set => ({
                    key: set.key,
                    name: set.name,
                    description: set.description,
                })),
            };
        },
    });
}


