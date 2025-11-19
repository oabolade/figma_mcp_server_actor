/**
 * Figma MCP Prompts
 * Prompts to guide AI assistants in working with Figma designs
 */

export function registerFigmaPrompts(protocol, _figmaClient) {
  // Design analysis workflow prompt
  protocol.registerPrompt("analyze_design_file", {
    description:
      "Guide for analyzing a Figma design file to extract structure, components, and design system information",
    arguments: [
      {
        name: "fileKey",
        description: "Figma file key to analyze",
        required: true,
      },
    ],
    handler: async (args) => {
      const { fileKey } = args;

      return {
        description:
          "Analyze a Figma design file to understand its structure and design system",
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `I want to analyze the Figma file ${fileKey}. Please help me understand:
1. The file structure and pages
2. Available components and component sets
3. Design tokens and styles
4. Component usage patterns

Start by using the analyze_file tool to get an overview, then use list_components to see all available components, and extract_styles to understand the design system.`,
            },
          },
        ],
      };
    },
  });

  // Component extraction guidance prompt
  protocol.registerPrompt("extract_components", {
    description:
      "Guide for extracting and documenting components from a Figma file",
    arguments: [
      {
        name: "fileKey",
        description: "Figma file key",
        required: true,
      },
      {
        name: "componentKey",
        description: "Specific component key to extract (optional)",
        required: false,
      },
    ],
    handler: async (args) => {
      const { fileKey, componentKey } = args;

      if (componentKey) {
        return {
          description:
            "Extract detailed information about a specific component",
          messages: [
            {
              role: "user",
              content: {
                type: "text",
                text: `Extract detailed information about component ${componentKey} from file ${fileKey}. Use get_component_details to get the component information, then find_component_usage to see where it's used in the file.`,
              },
            },
          ],
        };
      }

      return {
        description: "Extract and document all components from a Figma file",
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Extract all components from Figma file ${fileKey}. Use list_components to get all available components, then for each component use get_component_details to get detailed information and find_component_usage to understand usage patterns.`,
            },
          },
        ],
      };
    },
  });

  // Asset export best practices prompt
  protocol.registerPrompt("export_assets", {
    description:
      "Guide for exporting assets from Figma files in the appropriate formats",
    arguments: [
      {
        name: "fileKey",
        description: "Figma file key",
        required: true,
      },
      {
        name: "format",
        description: "Export format (PNG, SVG, PDF, JPG)",
        required: false,
      },
    ],
    handler: async (args) => {
      const { fileKey, format = "PNG" } = args;

      const formatGuidance = {
        PNG: "Use PNG for raster images, icons, and screenshots. Good for web use.",
        SVG: "Use SVG for vector graphics, icons, and scalable assets. Best for web and print.",
        PDF: "Use PDF for documents, presentations, and print-ready materials.",
        JPG: "Use JPG for photographs and images with many colors. Smaller file size than PNG.",
      };

      return {
        description: "Export assets from a Figma file",
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Export assets from Figma file ${fileKey} in ${format} format.

${formatGuidance[format] || "Choose the appropriate format based on your use case."}

Best practices:
- Use export_node for single assets
- Use export_multiple_nodes for batch exports
- Use export_file_pages to export entire pages
- For icons and logos, prefer SVG format
- For images and screenshots, use PNG or JPG
- Use appropriate scale factors (1x, 2x, 3x) for different display densities

Start by analyzing the file structure to identify which nodes to export.`,
            },
          },
        ],
      };
    },
  });

  // Design system consistency check prompt
  protocol.registerPrompt("check_design_system", {
    description:
      "Guide for checking design system consistency across a Figma file",
    arguments: [
      {
        name: "fileKey",
        description: "Figma file key to check",
        required: true,
      },
    ],
    handler: async (args) => {
      const { fileKey } = args;

      return {
        description: "Check design system consistency in a Figma file",
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Analyze the design system consistency in Figma file ${fileKey}.

Check for:
1. Component usage patterns - are components being reused or duplicated?
2. Style consistency - are design tokens being used consistently?
3. Naming conventions - are components and styles named consistently?
4. Component variants - are component sets being used properly?

Use extract_styles to get all design tokens, list_components to see all components, and find_component_usage to check component reuse patterns. Identify any inconsistencies or areas for improvement.`,
            },
          },
        ],
      };
    },
  });

  // Comment and feedback management prompt
  protocol.registerPrompt("manage_feedback", {
    description: "Guide for managing comments and feedback in Figma files",
    arguments: [
      {
        name: "fileKey",
        description: "Figma file key",
        required: true,
      },
    ],
    handler: async (args) => {
      const { fileKey } = args;

      return {
        description: "Manage comments and feedback in a Figma file",
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Help manage comments and feedback for Figma file ${fileKey}.

Use get_comments to retrieve all existing comments. You can create new comments using create_comment with either:
- X/Y coordinates for general file comments
- Node ID for comments attached to specific design elements

For each comment, provide context about what it relates to and help organize feedback for the design team.`,
            },
          },
        ],
      };
    },
  });
}
