import React from 'react';
import { Text, TextProps } from 'react-native';
import { colors } from '../constants/theme';

type Props = TextProps & { color?: string };

export default function ThemedText({ color, style, ...props }: Props) {
  return <Text style={[{ color: color || colors.text }, style]} {...props} />;
}
