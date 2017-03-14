#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

API_ACTIONS = {
    "WorkspaceCenter": {
        "Status": {     # 查看学习环境的状态，包括了启动状态和结束状态
            "action": ("workspace-center", "status", "get_workspace_status"),
            "login_required": True},

        "RequestBooting": {     # 请求开启学习环境
            "action": ("workspace-center", "boot", "to_boot_workspace"),
            "login_required": True},
        "RequestFinish": {      # 请求结束学习
            "action": ("workspace-center", "quit", "to_quit_workspace"),
            "login_required": True},
        "LoadTask": {     # 获取任务详情
            "action": ("workspace-center", "learning", "load_task"),
            "login_required": True},

        "SaveAndExec": {    # 保存和执行
            "action": ("workspace-center", "learning", "save_and_exec"),
            "login_required": True},
        "ResetLesson": {    # 重置当前课程服务器数据
            "action": ("workspace-center", "learning", "reset_lesson"),
            "login_required": True},
        "GotIt": {      # 标记当前Task为完成状态
            "action": ("workspace-center", "learning", "got_it"),
            "login_required": True},

        "CurrentStudyStatus": {    #
            "action": ("workspace-center", "learning", "load_study_status"),
            "login_required": True},
        "CurrentStudyTiming": {    #
            "action": ("workspace-center", "learning", "get_studying_timing"),
            "login_required": True},
    },
}


def load_workflow(api_key, api_action):
    """ 加载 API 的 Wrokflow """

    package, moduler, func = API_ACTIONS[api_key][api_action]["action"]
    workflow = getattr(
        __import__(
            "fuerte.api.v1.actions.%s.%s" % (package, moduler),
            fromlist=[func]
        ),
        func
    )

    return (0, "Success!", workflow)
