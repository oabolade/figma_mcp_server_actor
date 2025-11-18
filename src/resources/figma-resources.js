/**
 * Figma MCP Resources
 * Read-only resources for accessing Figma design data
 */

export function registerFigmaResources(protocol, figmaClient) {
    // File metadata resource
    protocol.registerResource('figma://file/{fileKey}', {
        name: 'Figma File',
        description: 'Access metadata and structure of a Figma design file',
        mimeType: 'application/json',
        handler: async (uri) => {
            const match = uri.match(/^figma:\/\/file\/(.+)$/);
            if (!match) {
                throw new Error(`Invalid file resource URI: ${uri}`);
            }

            const fileKey = match[1];
            const fileData = await figmaClient.getFile(fileKey);

            return {
                uri,
                fileKey,
                name: fileData.name,
                lastModified: fileData.lastModified,
                version: fileData.version,
                thumbnailUrl: fileData.thumbnailUrl,
                document: {
                    id: fileData.document.id,
                    type: fileData.document.type,
                    name: fileData.document.name,
                },
                pages: fileData.document.children?.map(page => ({
                    id: page.id,
                    name: page.name,
                    type: page.type,
                })) || [],
                componentsCount: Object.keys(fileData.components || {}).length,
                componentSetsCount: Object.keys(fileData.componentSets || {}).length,
                stylesCount: Object.keys(fileData.styles || {}).length,
            };
        },
    });

    // Components resource
    protocol.registerResource('figma://components/{fileKey}', {
        name: 'Figma Components',
        description: 'Access component library from a Figma file',
        mimeType: 'application/json',
        handler: async (uri) => {
            const match = uri.match(/^figma:\/\/components\/(.+)$/);
            if (!match) {
                throw new Error(`Invalid components resource URI: ${uri}`);
            }

            const fileKey = match[1];
            const fileData = await figmaClient.getFile(fileKey);

            const components = fileData.components || {};
            const componentSets = fileData.componentSets || {};

            return {
                uri,
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

    // Styles resource
    protocol.registerResource('figma://styles/{fileKey}', {
        name: 'Figma Styles',
        description: 'Access design tokens and styles from a Figma file',
        mimeType: 'application/json',
        handler: async (uri) => {
            const match = uri.match(/^figma:\/\/styles\/(.+)$/);
            if (!match) {
                throw new Error(`Invalid styles resource URI: ${uri}`);
            }

            const fileKey = match[1];
            const fileData = await figmaClient.getFile(fileKey);

            const styles = fileData.styles || {};

            const categorizedStyles = {
                fills: [],
                strokes: [],
                effects: [],
                text: [],
            };

            Object.values(styles).forEach(style => {
                const styleData = {
                    key: style.key,
                    name: style.name,
                    description: style.description || '',
                    styleType: style.styleType,
                };

                switch (style.styleType) {
                    case 'FILL':
                        categorizedStyles.fills.push(styleData);
                        break;
                    case 'STROKE':
                        categorizedStyles.strokes.push(styleData);
                        break;
                    case 'EFFECT':
                        categorizedStyles.effects.push(styleData);
                        break;
                    case 'TEXT':
                        categorizedStyles.text.push(styleData);
                        break;
                }
            });

            return {
                uri,
                fileKey,
                styles: categorizedStyles,
                totalCount: Object.keys(styles).length,
            };
        },
    });

    // Project resource
    protocol.registerResource('figma://project/{projectId}', {
        name: 'Figma Project',
        description: 'Access project information and file list',
        mimeType: 'application/json',
        handler: async (uri) => {
            const match = uri.match(/^figma:\/\/project\/(.+)$/);
            if (!match) {
                throw new Error(`Invalid project resource URI: ${uri}`);
            }

            const projectId = match[1];
            const projectFiles = await figmaClient.getProjectFiles(projectId);

            return {
                uri,
                projectId,
                files: projectFiles.files?.map(file => ({
                    key: file.key,
                    name: file.name,
                    thumbnailUrl: file.thumbnail_url,
                    lastModified: file.last_modified,
                    modifiedBy: file.modified_by,
                })) || [],
                filesCount: projectFiles.files?.length || 0,
            };
        },
    });

    // Team projects resource (helper resource)
    protocol.registerResource('figma://team/{teamId}/projects', {
        name: 'Team Projects',
        description: 'List all projects for a team',
        mimeType: 'application/json',
        handler: async (uri) => {
            const match = uri.match(/^figma:\/\/team\/(.+)\/projects$/);
            if (!match) {
                throw new Error(`Invalid team projects resource URI: ${uri}`);
            }

            const teamId = match[1];
            const projects = await figmaClient.getProjects(teamId);

            return {
                uri,
                teamId,
                projects: projects.projects?.map(project => ({
                    id: project.id,
                    name: project.name,
                })) || [],
                projectsCount: projects.projects?.length || 0,
            };
        },
    });
}


