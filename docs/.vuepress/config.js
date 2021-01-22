module.exports = {
    base: '',
    markdown: {
        lineNumbers: true, // 是否在每个代码块的左侧显示行号。
        // slugify:一个将标题文本转换为 slug 的函数。
        // anchor:markdown-it-anchor 的选项
        anchor: { permalink: false },
        toc: { includeLevel: [1, 2] }
    },
    locales: {
        '/en/': {
            lang: 'en-US',
            title: 'CustomBot | Online Document',
            description: 'This is a customized automated testing framework.',
        },
        '/': {
            lang: 'zh-CN',
            title: 'CustomBot | 在线文档',
            description: '这是一个可定制化的自动化测试框架.',
        }
    },
    themeConfig: {
        locales: {
            '/en/': {
                selectText: 'Languages',
                label: 'English',
                ariaLabel: 'Languages',
                editLinkText: 'Edit this page on GitHub',
                serviceWorker: {
                    updatePopup: {
                        message: 'New content is available.',
                        buttonText: 'Refresh'
                    }
                }
            },
            '/': {
                selectText: '选择语言',
                label: '简体中文',
                // 编辑链接文字
                editLinkText: '在 GitHub 上编辑此页',
                serviceWorker: {
                    updatePopup: {
                        message: '发现新内容可用.',
                        buttonText: '刷新'
                    }
                },
                lastUpdated: '上次更新: ',
                nav: [
                    { text: '首页', link: '/' },
                    { text: '业务工具库', link: '/sp-hotlib/' },
                    {
                        text: '接入文档',
                        link: '/guide/',
                        items: [
                            { text: '拨测系统', link: '/dialup/' },
                            { text: 'BirdFramework', link: '/bird/' },
                            { text: 'GoCoverage', link: '/go-cover/' },
                        ]
                    },
                    { text: '开发工具推荐', link: '/dev-tools/' },
                    { text: '文档编写', link: '/doc_ci' },
                    { text: '项目合集', link: 'https://git.garena.com/shopee/loan-service/qa/dev-sup' },
                ],
                sidebar: {}
            },
        }
    }
}