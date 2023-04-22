<script>
    import {
        Heading,
        Layout,
        Button,
        Select,
        Modal,
        Page,
        notifications,
        Notification,
        Body,
        Icon,
        Search,
        InlineAlert,
    } from "@budibase/bbui"
    import Spinner from "components/common/Spinner.svelte"
    import CreateAppModal from "components/start/CreateAppModal.svelte"
    import AppLimitModal from "components/portal/licensing/AppLimitModal.svelte"
    import ConfirmDialog from "components/common/ConfirmDialog.svelte"

    import {store, automationStore} from "builderStore"
    import {API} from "api"
    import {onMount} from "svelte"
    import {apps, auth, admin, licensing, environment} from "stores/portal"
    import {goto} from "@roxi/routify"
    import AppRow from "components/start/AppRow.svelte"
    import {AppStatus} from "constants"
    import Logo from "assets/bb-space-man.svg"

    let sortBy = "name"
    let template
    let creationModal
    let appLimitModal
    let creatingApp = false
    let searchTerm = ""
    let cloud = $admin.cloud
    let creatingFromTemplate = false
    let automationErrors
    let accessFilterList = null
    let confirmDownloadDialog

    $: welcomeHeader = `Welcome ${$auth?.user?.firstName || "back"}`
    $: enrichedApps = enrichApps($apps, $auth.user, sortBy)
    $: filteredApps = enrichedApps.filter(
        app =>
            (searchTerm
                ? app?.name?.toLowerCase().includes(searchTerm.toLowerCase())
                : true) &&
            (accessFilterList !== null
                ? accessFilterList?.includes(
                    `${app?.type}_${app?.tenantId}_${app?.appId}`
                )
                : true)
    )
    $: automationErrors = getAutomationErrors(enrichedApps)

    const enrichApps = (apps, user, sortBy) => {
        const enrichedApps = apps.map(app => ({
            ...app,
            deployed: app.status === AppStatus.DEPLOYED,
            lockedYou: app.lockedBy && app.lockedBy.email === user?.email,
            lockedOther: app.lockedBy && app.lockedBy.email !== user?.email,
        }))

        if (sortBy === "status") {
            return enrichedApps.sort((a, b) => {
                if (a.status === b.status) {
                    return a.name?.toLowerCase() < b.name?.toLowerCase() ? -1 : 1
                }
                return a.status === AppStatus.DEPLOYED ? -1 : 1
            })
        } else if (sortBy === "updated") {
            return enrichedApps.sort((a, b) => {
                const aUpdated = a.updatedAt || "9999"
                const bUpdated = b.updatedAt || "9999"
                return aUpdated < bUpdated ? 1 : -1
            })
        } else {
            return enrichedApps.sort((a, b) => {
                return a.name?.toLowerCase() < b.name?.toLowerCase() ? -1 : 1
            })
        }
    }

    const getAutomationErrors = apps => {
        const automationErrors = {}
        for (let app of apps) {
            if (app.automationErrors) {
                if (errorCount(app.automationErrors) > 0) {
                    automationErrors[app.devId] = app.automationErrors
                }
            }
        }
        return automationErrors
    }

    const goToAutomationError = appId => {
        const params = new URLSearchParams({
            open: "error",
        })
        $goto(`../overview/${appId}/automation-history?${params.toString()}`)
    }

    const errorCount = errors => {
        return Object.values(errors).reduce((acc, next) => acc + next.length, 0)
    }

    const automationErrorMessage = appId => {
        const app = enrichedApps.find(app => app.devId === appId)
        const errors = automationErrors[appId]
        return `${app.name} - Automation error (${errorCount(errors)})`
    }

    const initiateAppCreation = async () => {
        if ($licensing?.usageMetrics?.apps >= 100) {
            appLimitModal.show()
        } else if ($apps?.length) {
            $goto("/builder/portal/apps/create")
        } else {
            template = null
            creationModal.show()
            creatingApp = true
        }
    }

    const initiateAppsExport = () => {
        try {
            window.location = `/api/cloud/export`
            notifications.success("Apps exported successfully")
        } catch (err) {
            notifications.error(`Error exporting apps: ${err}`)
        }
    }

    const initiateAppImport = () => {
        template = {fromFile: true}
        creationModal.show()
        creatingApp = true
    }

    const autoCreateApp = async () => {
        try {
            // Auto name app if has same name
            const templateKey = template.key.split("/")[1]

            let appName = templateKey.replace(/-/g, " ")
            const appsWithSameName = $apps.filter(app =>
                app.name?.startsWith(appName)
            )
            appName = `${appName} ${appsWithSameName.length + 1}`

            // Create form data to create app
            let data = new FormData()
            data.append("name", appName)
            data.append("useTemplate", true)
            data.append("templateKey", template.key)

            // Create App
            const createdApp = await API.createApp(data)

            // Select Correct Application/DB in prep for creating user
            const pkg = await API.fetchAppPackage(createdApp.instance._id)
            await store.actions.initialise(pkg)
            await automationStore.actions.fetch()
            // Update checklist - in case first app
            await admin.init()

            // Create user
            await API.updateOwnMetadata({
                roleId: "BASIC",
            })
            await auth.setInitInfo({})
            $goto(`/builder/app/${createdApp.instance._id}`)
        } catch (error) {
            notifications.error("Error creating app")
        }
    }

    const stopAppCreation = () => {
        template = null
        creatingApp = false
    }

    function createAppFromTemplateUrl(templateKey) {
        // validate the template key just to make sure
        const templateParts = templateKey.split("/")
        if (templateParts.length === 2 && templateParts[0] === "app") {
            template = {
                key: templateKey,
            }
            autoCreateApp()
        } else {
            notifications.error("Your Template URL is invalid. Please try another.")
        }
    }

    onMount(async () => {
        try {
            await environment.loadVariables()
            // If the portal is loaded from an external URL with a template param
            const initInfo = await auth.getInitInfo()
            if (initInfo?.init_template) {
                creatingFromTemplate = true
                createAppFromTemplateUrl(initInfo.init_template)
            }
        } catch (error) {
            notifications.error("Error getting init info")
        }
    })

    let messageInput = "";
    let messages = [];

    let taskList = [];

    function sendMessage() {
        if (messageInput.trim()) {

            messages = [...messages, {text: messageInput.trim(), timestamp: new Date(), isUser: true}];
            let inputText = messageInput;

            messageInput = "";


            // messages = [...messages, {text: '正在为您构建应用，请稍等', timestamp: new Date(), isUser: false}];
            //
            // messages = [...messages, {text: '正在部署测试环境，请稍等', timestamp: new Date(), isUser: false}];
            //
            // messages = [...messages, {
            //     text: '应用构建完毕，访问地址：<a href="http://localhost:10000/app_dev_3f5f2a0c100b45d3af9f142bfa1f7972#/" target="_blank">IT Asset Management Software</a>',
            //     timestamp: new Date(),
            //     isUser: false
            // }];

            messages = [...messages, {text: '正在需求分析，请稍等...', timestamp: new Date(), isUser: false}];

            startGoalChat(inputText)
                .then(response => {

                    messages = [...messages, {text: '需求分析已完成', timestamp: new Date(), isUser: false}];

                    messages = [...messages, {text: '正在为您创建应用，请稍等片刻...', timestamp: new Date(), isUser: false}];

                    messages = [...messages, {text: '正在为您创建任务，请稍等片刻...', timestamp: new Date(), isUser: false}];

                    let newSchemaTaskList = response.schema.map((schemaItem) => {
                        return {
                            title: schemaItem.taskName,
                            tasks: [
                                {name: schemaItem.taskGoal, type: 'schema'}
                            ]
                        }
                    });
                    taskList = taskList.concat(newSchemaTaskList);
                    messages = [...messages, {text: '创建数据结构设计任务已完成', timestamp: new Date(), isUser: false}];

                    let newViewTaskList = response.view.map((schemaItem) => {
                        return {
                            title: schemaItem.taskName,
                            tasks: [
                                {name: schemaItem.taskGoal, type: 'view'}
                            ]
                        }
                    });
                    taskList = taskList.concat(newViewTaskList);
                    messages = [...messages, {text: '创建页面设计任务已完成', timestamp: new Date(), isUser: false}];

                    messages = [...messages, {
                        text: 'MindForge AI 开始自动执行任务，请稍等片刻...',
                        timestamp: new Date(),
                        isUser: false
                    }];


                    let newTaskList = Object.assign([], taskList);
                    for (let i = 0; i < newTaskList.length; i++) {
                        let taskItem = newTaskList[i];
                        let title = taskItem.title;
                        messages = [...messages, {
                            text: title + '执行完毕，继续下一个任务',
                            timestamp: new Date(),
                            isUser: false
                        }];
                        taskList = taskList.filter(task => task.title !== title);
                    }

                })
                .catch(error => {
                    console.error(error);
                });
        }
    }

    function startGoalChat(prompt) {
        return fetch(`http://localhost:8000/app/startGoalChat?prompt=${prompt}`)
            .then(res => res.json())
            .then(data => data.response);
    }

    function executeSchemaTaskChat(goal, taskName, taskGoal, taskHought) {
        return fetch('http://127.0.0.1:8000/app/executeSchemaTaskChat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                goal: goal,
                taskName: taskName,
                taskGoal: taskGoal,
                taskHought: taskHought
            })
        })
            .then(res => res.json())
            .then(data => data.response);
    }

    function handleKeyDown(e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    }


</script>

{#if $apps.length}
    <Page>
        <Layout noPadding gap="L">
            {#each Object.keys(automationErrors || {}) as appId}
                <Notification
                        wide
                        dismissable
                        action={() => goToAutomationError(appId)}
                        type="error"
                        icon="Alert"
                        actionMessage={errorCount(automationErrors[appId]) > 1
            ? "View errors"
            : "View error"}
                        on:dismiss={async () => {
            await automationStore.actions.clearLogErrors({ appId })
            await apps.load()
          }}
                        message={automationErrorMessage(appId)}
                />
            {/each}
            <div class="title">
                <div class="welcome">
                    <Layout noPadding gap="XS">
                        <Heading size="L">MindForge</Heading>
                        <Body size="M">
                        MindForge是一种智能技术，它可以帮助人们更快地构建自己的业务系统。它通过融合机器学习、自然语言处理和智能分析，提供了一种更高效的需求分析方式，可以更好的理解人们的业务需求。MindForge的核心理念是帮助人们更快地构建业务系统，更快地实现他们的目标。
                        </Body>
                    </Layout>
                </div>
            </div>

            {#if enrichedApps.length}
                <Layout noPadding gap="L">

                    <div class="chat-container-with-task-list">

                        <div class="chat-container">

                            <div class="chat-messages">
                                {#each messages as message (message.timestamp)}
                                    <div class="message {message.isUser ? 'message-right' : 'message-left'}">
                                        <div class="message-content {message.isUser ? 'user' : 'other'}">
                                            <span>{@html message.text}</span>
                                        </div>
                                    </div>
                                {/each}
                            </div>

                            <div class="chat-input">
                                <input
                                        type="text"
                                        bind:value="{messageInput}"
                                        placeholder="请简短描述一下你的需求~"
                                        on:keydown="{handleKeyDown}"
                                />
                                <button on:click="{sendMessage}">Send</button>
                            </div>

                        </div>

                        <div class="task-list-container">
                            <div class="task-list-header">
                                <i class="icon-task-list fa fa-list-alt"></i>
                                <h3>当前任务列表</h3>
                            </div>
                            <div class="task-item-container">
                                {#each taskList as task}
                                    <div class="task-list">
                                        <h2>{task.title}</h2>
                                        <ul>
                                            {#each task.tasks as item, i}
                                                <li>
                                                    <span class="task-name">目标：{item.name}</span>
                                                </li>
                                            {/each}
                                        </ul>
                                    </div>
                                {/each}
                            </div>
                        </div>

                    </div>

                </Layout>
            {/if}

            {#if creatingFromTemplate}
                <div class="empty-wrapper">
                    <img class="img-logo img-size" alt="logo" src={Logo}/>
                    <p>Creating your Budibase app from your selected template...</p>
                    <Spinner size="10"/>
                </div>
            {/if}
        </Layout>
    </Page>
{/if}

<Modal
        bind:this={creationModal}
        padding={false}
        width="600px"
        on:hide={stopAppCreation}
>
    <CreateAppModal {template}/>
</Modal>

<AppLimitModal bind:this={appLimitModal}/>

<ConfirmDialog
        bind:this={confirmDownloadDialog}
        okText="Continue"
        onOk={initiateAppsExport}
        warning={false}
        title="Download all apps"
>
    <InlineAlert
            header="Do not share your budibase application exports publicly as they may contain sensitive information such as database credentials or secret keys."
    />
</ConfirmDialog>

<style>
    .title {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        gap: var(--spacing-xl);
        flex-wrap: wrap;
    }

    .buttons {
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: center;
        gap: var(--spacing-xl);
        flex-wrap: wrap;
    }

    .app-actions {
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: center;
        gap: var(--spacing-xl);
        flex-wrap: wrap;
    }

    .app-actions :global(.spectrum-Textfield) {
        max-width: 180px;
    }

    .app-table {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: stretch;
        gap: var(--spacing-xl);
        overflow: hidden;
    }

    .empty-wrapper {
        flex: 1 1 auto;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .img-size {
        width: 160px;
        height: 160px;
    }

    @media (max-width: 1000px) {
        .img-logo {
            display: none;
        }
    }

    @media (max-width: 640px) {
        .app-actions {
            margin-top: var(--spacing-xl);
            margin-bottom: calc(-1 * var(--spacing-m));
        }

        .app-actions :global(.spectrum-Textfield) {
            max-width: none;
        }

        /*  Hide download apps icon */
        .app-actions :global(> .spectrum-Icon) {
            display: none;
        }

        .app-actions > :global(*) {
            flex: 1 1 auto;
        }
    }

    /* chat */

    :global(body) {
        background-color: #222;
        color: #eee;
        font-family: Arial, sans-serif;
    }


    .chat-messages {
        flex-grow: 1;
        overflow-y: auto;
        margin-bottom: 1rem;
    }

    .chat-input {
        display: flex;
    }

    input, button {
        border: none;
        outline: none;
        background-color: #333;
        color: #eee;
        padding: 0.5rem;
    }

    input {
        flex-grow: 1;
        border-radius: 4px 0 0 4px;
    }

    button {
        border-radius: 0 4px 4px 0;
    }

    .message {
        display: flex;
        margin-bottom: 0.5rem;
    }

    .message-left {
        justify-content: flex-start;
    }

    .message-right {
        justify-content: flex-end;
    }

    .message-content {
        padding: 0.5rem;
        border-radius: 4px;
        max-width: 70%;
    }

    .message-content.user {
        background-color: #555;
    }

    .message-content.other {
        background-color: #444;
    }

    .chat-container-with-task-list {
        display: flex;

    }

    .chat-container {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 60vh;
        width: 70%;
        padding: 1rem;
        border: 1px solid #dcdcdc;
        border-radius: 10px;
        box-shadow: 0px 5px 20px rgba(255, 255, 255, 0.1);
        margin-right: 10px;
        background-color: #000;
    }

    .task-list-container {
        width: 30%;
        border: 1px solid #dcdcdc;
        border-radius: 10px;
        background-color: #000;
        margin-right: 10px;
        background-color: #000;
    }

    .task-item-container {
        max-height: 60vh; /* 设置最大高度 */
        height: 60vh; /* 设置固定高度 */
        overflow-y: auto; /* 允许出现纵向滚动条 */
    }

    .task-list-header {
        display: flex;
        height: 20px;
        align-items: center;
        justify-content: center;
        margin-top: 5px;
    }

    .icon-task-list {
        font-size: 1rem;
        margin-right: 10px;
    }

    .task-list {
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        margin: 10px;
        background-color: #222;
    }

    .task-list h2 {
        margin-top: 0;
        margin-bottom: 10px;
        font-size: 1.2rem;
        font-weight: bold;
    }

    .task-list ul {
        padding-left: 0;
        list-style: none;
    }

    .task-list li {
        margin-bottom: 5px;
        font-size: 1rem;
        color: #fff;
    }

    .task-list li .task-name {
        font-weight: bold;
    }

    .task-list li .task-desc {
        margin-left: 10px;
    }

</style>
