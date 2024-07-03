import React, { useState, useEffect } from 'react';
import { Layout, message } from 'antd';
import { v4 as uuidv4 } from 'uuid';
import TextAreaUpload from './components/TextAreaUpload';
import VideoTabs from './components/VideoTabs';

const { Content, Footer, Header } = Layout;

const App = () => {
  const [videoClips, setVideoClips] = useState([]);
  const [videoClips2, setVideoClips2] = useState([]);
  const uniqueID = uuidv4();
  const POLL_INTERVAL = 5000; // 每5秒轮询一次
  const TIMEOUT = 60000; // 总超时时间 10 分钟

  const pollData = async (fetchFunction, setDataFunction, id, dataKey) => {
    const endTime = Date.now() + TIMEOUT;
    let hasFetched = false;

    const poll = async () => {
      try {
        const response = await fetchFunction(id);
        if (response.ok) {
          const result = await response.json();

          if (result.msg === 'done') {
            if (result[dataKey] && result[dataKey].length > 0) {
              setDataFunction(result[dataKey].map(item => ({
                ...item,
                url: item.file_path,
                tags: item.tags || [],
                description: item.description || '',
              })));
              hasFetched = true; // 成功获取数据后停止轮询
              return;
            }
          }  // no else
        } else {
          message.error('Failed to fetch data');
        }
      } catch (error) {
        console.error('Polling error:', error);
        message.error('Polling error');
      }

      if (Date.now() < endTime && !hasFetched) {
        setTimeout(poll, POLL_INTERVAL);
      } else if (!hasFetched) {
        message.error('Polling timed out');
      }
    };

    await poll();
  };

  const fetchDataForTab1 = async (id) => {
    return fetch(`/api/v1/extract/${id}/llm_srts`);
  };

  const fetchDataForTab2 = async (id) => {
    return fetch(`/api/v1/extract/${id}/imgs_info`);
  };

  useEffect(() => {
    pollData(fetchDataForTab1, setVideoClips, uniqueID, 'llm_srts')
      .catch(error => console.error('Tab 1 polling error:', error));

    pollData(fetchDataForTab2, setVideoClips2, uniqueID, 'imgs_info')
      .catch(error => console.error('Tab 2 polling error:', error));
  }, [uniqueID]);

  const handleUploadSuccess = async (id) => {
    try {
      await pollData(fetchDataForTab1, setVideoClips, id, 'llm_srts');
      await pollData(fetchDataForTab2, setVideoClips2, id, 'imgs_info');
    } catch (error) {
      console.error('Upload success polling error:', error);
    }
  };

  return (
    <Layout>
      <Header>
        <h1 style={{ color: 'white' }}>SceneSpark</h1>h1>
      </Header>
      <Content style={{ padding: '20px' }}>
        <TextAreaUpload uniqueID={uniqueID} onUploadSuccess={handleUploadSuccess} />
        <VideoTabs
          videoClips={videoClips}
          videoClips2={videoClips2}
        />
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        SceneSpark ©2024 Created by methanal
      </Footer>
    </Layout>
  );
};

export default App;
