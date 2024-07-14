import React, { useState } from 'react';
import { Alert, Divider, Layout, message, Tabs, Upload } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { v4 as uuidv4 } from 'uuid';
import Marquee from 'react-fast-marquee';
import TextAreaAfterLLM from './components/TextAreaAfterLLM';
import TextAreaBeforeLLM from './components/TextAreaBeforeLLM';
import VideoTabs from './components/VideoTabs';
import VideoTabBeforeLLM from './components/VideoTabBeforeLLM';

const { Content, Footer, Header } = Layout;
const { TabPane } = Tabs;
const { Dragger } = Upload;

const App = () => {
  const [videoClips, setVideoClips] = useState([]);
  const [videoClips2, setVideoClips2] = useState([]);
  const [videoClips3, setVideoClips3] = useState([]);
  const [videoClips4, setVideoClips4] = useState([]);
  const [uniqueID] = useState(uuidv4());
  const [isFileUploaded, setIsFileUploaded] = useState(false);

  const handleUpload = (file) => {
    const formData = new FormData();
    formData.append('files', file);
    formData.append('request_id', uniqueID);

    // 自定义上传请求
    fetch('/api/v1/upload', {
      method: 'POST',
      body: formData,
    })
      .then(response => response.json())
      .then(data => {
        message.success(`${file.name} file uploaded successfully.`);
        console.log(data);
        setIsFileUploaded(true);
      })
      .catch(() => {
        message.error(`${file.name} file upload failed.`);
      });

    // 返回 false 以阻止默认上传行为
    return false;
  };

  const props = {
    name: 'file',
    multiple: true,
    beforeUpload: handleUpload,
    onChange(info) {
      const { status } = info.file;
      if (status !== 'uploading') {
        console.log(info.file, info.fileList);
      }
      if (status === 'done') {
        message.success(`${info.file.name} file uploaded successfully.`);
      } else if (status === 'error') {
        message.error(`${info.file.name} file upload failed.`);
      }
    },
    onDrop(e) {
      console.log('Dropped files', e.dataTransfer.files);
    },
  };

  const handleFetchTab1 = async (prompt, translationModel, modelSize, whisperPrompt) => {
    if (!isFileUploaded) {
      message.error('Please upload a file first.');
      return;
    }

    try {
      const response = await fetch(`/api/v1/clips/extract/llm_srts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ request_id: uniqueID, translation_model: translationModel, model_size: modelSize, whisper_prompt: whisperPrompt, prompt }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.llm_srts && result.llm_srts.length > 0) {
          setVideoClips(result.llm_srts.map(item => ({
            ...item,
            url: item.file_path,
            tags: item.tags || [],
            description: item.description || '',
          })));
          return;
        }
      } else {
        message.error('Failed to fetch data');
      }
    } catch (error) {
      console.error('Polling error:', error);
      message.error('Polling error');
    }
  };

  const handleFetchTab2 = async (prompt, samplingInterval, clipDuration) => {
    if (!isFileUploaded) {
      message.error('Please upload a file first.');
      return;
    }

    try {
      const response = await fetch(`/api/v1/clips/extract/imgs_info`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ request_id: uniqueID, sample_interval: samplingInterval, clip_duration: clipDuration, prompt }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.imgs_info && result.imgs_info.length > 0) {
          setVideoClips2(result.imgs_info.map(item => ({
            ...item,
            url: item.file_path,
            tags: item.tags || [],
            description: item.description || '',
          })));
          return;
        }
      } else {
        message.error('Failed to fetch data');
      }
    } catch (error) {
      console.error('Polling error:', error);
      message.error('Polling error');
    }
  };

  const handleFetchTab3 = async () => {
    if (!isFileUploaded) {
      message.error('Please upload a file first.');
      return;
    }

    try {
      const response = await fetch(`/api/v1/clips/merge_json`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ request_id: uniqueID }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.merge_json && result.merge_json.length > 0) {
          setVideoClips3(result.merge_json.map(item => ({
            ...item,
            url: item.file_path,
            tags: item.tags || [],
            description: item.description || '',
          })));
          return;
        }
      } else {
        message.error('Failed to fetch data');
      }
    } catch (error) {
      console.error('Polling error:', error);
      message.error('Polling error');
    }
  };

  const handleFetchTab4 = async (translationModel, modelSize, whisperPrompt, samplingInterval, clipDuration, prompt) => {
    if (!isFileUploaded) {
      message.error('Please upload a file first.');
      return;
    }

    try {
      const response = await fetch(`/api/v1/clips/extract/vision_with_srt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          request_id: uniqueID,
          translation_model: translationModel,
          model_size: modelSize,
          whisper_prompt: whisperPrompt,
          sample_interval: samplingInterval,
          clip_duration: clipDuration,
          prompt
        }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.vision_with_srt_json && result.vision_with_srt_json.length > 0) {
          setVideoClips4(result.vision_with_srt_json.map(item => ({
            ...item,
            url: item.file_path,
            tags: item.tags || [],
            description: item.description || '',
          })));
          return;
        }
      } else {
        message.error('Failed to fetch data');
      }
    } catch (error) {
      console.error('Polling error:', error);
      message.error('Polling error');
    }
  };

  return (
    <Layout>
      <Header style={{ height: '40px', lineHeight: '40px', padding: '0 20px' }}>
      </Header>
      <Content style={{ padding: '20px' }}>
        <Dragger {...props}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">Click or drag file to this area to upload</p>
          <p className="ant-upload-hint">
            Support for a single or bulk upload. Strictly prohibited from uploading company data or other
            banned files.
          </p>
        </Dragger>
        <Divider />
        <Tabs type="card" defaultActiveKey="2">
          <TabPane tab="LLM picks audio and vision separately" key="1">
            <Alert
              banner
              message={
                <Marquee pauseOnHover gradient={false}>
                  Subtitle Clipper 和 LLM Vision Clipper 分别切片，之后也可以基于两者的中间 JSON 重新合并切片。
                </Marquee>
              }
            />
            <TextAreaAfterLLM
              uniqueID={uniqueID}
              handleFetchTab1={handleFetchTab1}
              handleFetchTab2={handleFetchTab2}
            />
            <VideoTabs
              videoClips={videoClips}
              videoClips2={videoClips2}
              videoClips3={videoClips3}
              handleFetchTab3={handleFetchTab3}
            />
          </TabPane>
          <TabPane tab="LLM picks from video meta json" key="2">
            <Alert
              banner
              message={
                <Marquee pauseOnHover gradient={false}>
                  先使用 Subtitle Clipper 抽取 Subtitle JSON，然后 LLM Vision 拉片时参考 Subtitle JSON，最后将集成了 Subtitle 的采样，发给 LLM 筛选。
                </Marquee>
              }
            />
            <TextAreaBeforeLLM
              uniqueID={uniqueID}
              handleFetchTab4={handleFetchTab4}
            />
            <VideoTabBeforeLLM
              videoClips4={videoClips4}
            />
          </TabPane>
        </Tabs>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
      </Footer>
    </Layout>
  );
};

export default App;
