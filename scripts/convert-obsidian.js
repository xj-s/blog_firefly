import fs from 'fs';
import path from 'path';

const POSTS_DIR = './src/content/posts';

// 转换 Obsidian 语法为标准 Markdown
function convertObsidianSyntax(content, filePath) {
  let converted = content;
  const fileDir = path.dirname(filePath);

  // 1. 转换图片语法: ![[图片.png]] 或 ![[图片.png|尺寸]] -> ![图片](images/图片.png)
  converted = converted.replace(/!\[\[([^\]|]+)(?:\|(\d+))?\]\]/g, (match, imageName, size) => {
    // 检查图片是否存在
    const possiblePaths = [
      path.join(fileDir, imageName),
      path.join(fileDir, 'images', imageName),
      path.join(POSTS_DIR, 'images', imageName),
    ];

    let imagePath = null;
    for (const p of possiblePaths) {
      if (fs.existsSync(p)) {
        imagePath = path.relative(fileDir, p).replace(/\\/g, '/');
        break;
      }
    }

    // 如果找不到图片，默认使用 images/ 子目录
    if (!imagePath) {
      imagePath = `images/${imageName}`;
    }

    const altText = imageName.replace(/\.[^.]+$/, '');
    return `![${altText}](${imagePath})`;
  });

  // 1.5 清理已转换但带尺寸的图片: ![alt](path|size) -> ![alt](path)
  converted = converted.replace(/!\[([^\]]*)\]\(([^)]+)\|(\d+)\)/g, '![$1]($2)');

  // 2. 转换高亮语法: ==文字== -> <mark>文字</mark>
  converted = converted.replace(/==([^=]+)==/g, '<mark>$1</mark>');

  return converted;
}

// 递归处理目录中的所有 .md 文件
function processDirectory(dir) {
  const files = fs.readdirSync(dir);

  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      // 跳过 Templates 目录
      if (file === 'Templates' || file === '.Templates') continue;
      processDirectory(filePath);
    } else if (file.endsWith('.md') || file.endsWith('.mdx')) {
      const content = fs.readFileSync(filePath, 'utf-8');
      const converted = convertObsidianSyntax(content, filePath);

      if (content !== converted) {
        fs.writeFileSync(filePath, converted, 'utf-8');
        console.log(`✅ Converted: ${filePath}`);
      }
    }
  }
}

console.log('🔄 Converting Obsidian syntax...');
processDirectory(POSTS_DIR);
console.log('✅ Conversion complete!');
