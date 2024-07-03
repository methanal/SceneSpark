import React from 'react';
import { Tabs, Descriptions, Tag, Row, Col } from 'antd';
import ReactPlayer from 'react-player';
import VideoClipList from './VideoClipList';

const { TabPane } = Tabs;

const VideoTabs = ({ videoClips, videoClips2, onClipClick, selectedClip }) => {
  return (
    <Row gutter={16}>
      <Col span={12}>
        <Tabs defaultActiveKey="1">
          <TabPane tab="LLM SRTS" key="1">
            <VideoClipList videoClips={videoClips} onClipClick={onClipClick} />
            {selectedClip && (
              <div style={{ marginTop: '20px' }}>
                <ReactPlayer url={selectedClip.url} controls />
                <Descriptions title="Video Clip Details" bordered>
                  <Descriptions.Item label="Description">{selectedClip.description}</Descriptions.Item>
                  <Descriptions.Item label="Tags">
                    {selectedClip.tags.map(tag => (
                      <Tag key={tag}>{tag}</Tag>
                    ))}
                  </Descriptions.Item>
                  <Descriptions.Item label="JSON">
                    <pre>{JSON.stringify(selectedClip, null, 2)}</pre>
                  </Descriptions.Item>
                </Descriptions>
              </div>
            )}
          </TabPane>
        </Tabs>
      </Col>
      <Col span={12}>
        <Tabs defaultActiveKey="1">
          <TabPane tab="LLM SRTS 2" key="1">
            <VideoClipList videoClips={videoClips2} onClipClick={onClipClick} />
            {selectedClip && (
              <div style={{ marginTop: '20px' }}>
                <ReactPlayer url={selectedClip.url} controls />
                <Descriptions title="Video Clip Details" bordered>
                  <Descriptions.Item label="Description">{selectedClip.description}</Descriptions.Item>
                  <Descriptions.Item label="Tags">
                    {selectedClip.tags.map(tag => (
                      <Tag key={tag}>{tag}</Tag>
                    ))}
                  </Descriptions.Item>
                  <Descriptions.Item label="JSON">
                    <pre>{JSON.stringify(selectedClip, null, 2)}</pre>
                  </Descriptions.Item>
                </Descriptions>
              </div>
            )}
          </TabPane>
        </Tabs>
      </Col>
    </Row>
  );
};

export default VideoTabs;
