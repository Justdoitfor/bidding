<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '../api/request'
import { ElMessage } from 'element-plus'

const activeTab = ref('history')
const historyData = ref([])
const tableType = ref('company')

// Fetch History
const fetchAllHistory = async () => {
  try {
    const res: any = await request.get('/chat/admin/history')
    historyData.value = res.map((session: any) => {
      return {
        session_id: session.session_id,
        user_id: session.user_id,
        title: session.title,
        created_at: session.created_at,
        msgCount: session.messages.length
      }
    })
  } catch (error) {
    console.error('Failed to load history', error)
  }
}

onMounted(() => {
  fetchAllHistory()
})

const handleUploadSuccess = (response: any) => {
  ElMessage.success(`文件上传成功，共导入 ${response.records_inserted} 条数据`)
}

const handleUploadError = (err: any) => {
  ElMessage.error(`上传失败: ${err.message || '未知错误'}`)
}
</script>

<template>
  <el-card>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="问答历史记录" name="history">
        <el-table :data="historyData" border style="width: 100%" height="400">
          <el-table-column prop="session_id" label="会话ID" width="300" />
          <el-table-column prop="user_id" label="用户ID" width="150" />
          <el-table-column prop="title" label="提问主题" />
          <el-table-column prop="created_at" label="创建时间" width="200" />
          <el-table-column prop="msgCount" label="消息数" width="100" />
        </el-table>
        <el-button style="margin-top: 10px;" @click="fetchAllHistory">刷新记录</el-button>
      </el-tab-pane>

      <el-tab-pane label="系统文档库更新" name="documents">
        <div style="margin-bottom: 20px;">
          <h3>上传 CSV 初始化数据</h3>
          <el-alert title="请根据 /data 目录下的数据库文档格式准备CSV文件" type="info" :closable="false" show-icon />
        </div>
        
        <el-form label-width="120px" style="max-width: 500px;">
          <el-form-item label="目标数据表">
            <el-select v-model="tableType" placeholder="请选择导入的目标库">
              <el-option label="企业信息库 (mysql_company)" value="company" />
              <el-option label="法律法规库 (mysql_law)" value="law" />
              <el-option label="商品信息库 (mysql_product)" value="product" />
              <el-option label="招标信息库 (mysql_zhaobiao)" value="zhaobiao" />
              <el-option label="中标信息库 (mysql_zhongbiao)" value="zhongbiao" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="上传数据源">
            <el-upload
              class="upload-demo"
              action="http://localhost:8000/api/v1/documents/upload"
              :data="{ table_type: tableType }"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              accept=".csv"
              :limit="1"
            >
              <el-button type="primary">点击上传 CSV 文件</el-button>
              <template #tip>
                <div class="el-upload__tip">
                  只能上传 csv 文件，且字段需与数据表结构对应
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>
