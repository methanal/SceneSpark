import React from 'react';
import { List, Card } from 'antd';

const VideoClipList = ({ videoClips, onClipClick }) => {
  return (
    <List
      grid={{ gutter: 16, column: 6 }}
      dataSource={videoClips}
      renderItem={clip => (
        <List.Item>
          <Card
            hoverable
            cover={<video src={clip.url} style={{ width: '100%' }} />}
            onClick={() => onClipClick(clip)}
          >
            <Card.Meta title="Video Clip" />
          </Card>
        </List.Item>
      )}
    />
  );
};

export default VideoClipList;
