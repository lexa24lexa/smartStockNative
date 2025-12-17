import React from 'react';
import { View, ViewProps } from 'react-native';
import { colors } from '../constants/theme';

type Props = ViewProps & { backgroundColor?: string };

export default function ThemedView({ backgroundColor, style, ...props }: Props) {
  return <View style={[{ backgroundColor: backgroundColor || colors.background }, style]} {...props} />;
}
