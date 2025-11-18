/**
 * Comment Management Tools
 * MCP tools for managing comments and feedback in Figma files
 */

export function registerCommentTools(protocol, figmaClient) {
    // Get comments
    protocol.registerTool('get_comments', {
        description: 'Retrieve all comments from a Figma file',
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
            
            const commentsData = await figmaClient.getComments(fileKey);

            return {
                fileKey,
                comments: commentsData.comments || [],
            };
        },
    });

    // Create comment
    protocol.registerTool('create_comment', {
        description: 'Create a new comment on a Figma file at a specific position or node',
        inputSchema: {
            type: 'object',
            properties: {
                fileKey: {
                    type: 'string',
                    description: 'Figma file key',
                },
                message: {
                    type: 'string',
                    description: 'Comment message text',
                },
                x: {
                    type: 'number',
                    description: 'X coordinate for comment position (required if node_id not provided)',
                },
                y: {
                    type: 'number',
                    description: 'Y coordinate for comment position (required if node_id not provided)',
                },
                nodeId: {
                    type: 'string',
                    description: 'Node ID to attach comment to (alternative to x/y coordinates)',
                },
            },
            required: ['fileKey', 'message'],
        },
        handler: async (args) => {
            const { fileKey, message, x, y, nodeId } = args;
            
            if (!nodeId && (x === undefined || y === undefined)) {
                throw new Error('Either nodeId or both x and y coordinates must be provided');
            }

            const commentData = {
                message,
                client_meta: nodeId
                    ? { node_id: nodeId }
                    : { x, y },
            };

            const result = await figmaClient.postComment(fileKey, commentData);

            return {
                fileKey,
                comment: result,
                success: true,
            };
        },
    });

    // Resolve comment
    protocol.registerTool('resolve_comment', {
        description: 'Mark a comment as resolved (Note: This may require Plugin API, currently returns info)',
        inputSchema: {
            type: 'object',
            properties: {
                fileKey: {
                    type: 'string',
                    description: 'Figma file key',
                },
                commentId: {
                    type: 'string',
                    description: 'Comment ID to resolve',
                },
            },
            required: ['fileKey', 'commentId'],
        },
        handler: async (args) => {
            const { fileKey, commentId } = args;
            
            // Note: Comment resolution via REST API may be limited
            // This is a placeholder for the functionality
            // Actual implementation may require Plugin API or webhook handling
            
            return {
                fileKey,
                commentId,
                message: 'Comment resolution via REST API may be limited. Please use Figma interface or Plugin API for full functionality.',
                note: 'This feature may require additional API endpoints or Plugin API integration',
            };
        },
    });

    // Delete comment (placeholder - may not be available via REST API)
    protocol.registerTool('delete_comment', {
        description: 'Delete a comment (Note: May require Plugin API or may not be available via REST)',
        inputSchema: {
            type: 'object',
            properties: {
                fileKey: {
                    type: 'string',
                    description: 'Figma file key',
                },
                commentId: {
                    type: 'string',
                    description: 'Comment ID to delete',
                },
            },
            required: ['fileKey', 'commentId'],
        },
        handler: async (args) => {
            const { fileKey, commentId } = args;
            
            // Note: Comment deletion via REST API may not be available
            // This is a placeholder
            
            return {
                fileKey,
                commentId,
                message: 'Comment deletion may not be available via REST API. Please use Figma interface or Plugin API.',
                note: 'This feature may require Plugin API integration',
            };
        },
    });
}


