import type { AnnouncementConfig } from "../types/config";

export const announcementConfig: AnnouncementConfig = {
	// 公告标题
	title: "考研倒计时",

	// 公告内容（留空，使用动态倒计时）
	content: "",

	// 是否允许用户关闭公告
	closable: true,

	link: {
		// 启用链接
		enable: true,
		// 链接文本
		text: "研招网",
		// 链接 URL
		url: "https://yz.chsi.com.cn/",
		// 外部链接
		external: true,
	},
};
